"""
api/chirps.py
CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)
rainfall estimates, sourced directly from **Google Earth Engine's**
`UCSB-CHG/CHIRPS/DAILY` ImageCollection - the canonical, actively
maintained CHIRPS archive (daily, ~5.5 km resolution, 1981-present).

This replaces the earlier ClimateSERV-based connector: GEE gives GEOAI-
grade access (server-side raster reduction over arbitrary
points/polygons) rather than a third-party REST wrapper.

## Authentication

Configure ONE of the following in `.env`:

1. Service account (recommended for servers/CI/Docker):
     GEE_SERVICE_ACCOUNT_EMAIL=my-sa@my-project.iam.gserviceaccount.com
     GEE_SERVICE_ACCOUNT_KEY_FILE=/secure/path/to/key.json
     GEE_PROJECT_ID=my-gcp-project

2. User/local dev, after running `earthengine authenticate` once:
     GEE_PROJECT_ID=my-gcp-project

If Earth Engine is not installed, not authenticated, or the query
fails for any reason (quota, connectivity, invalid geometry), this
client transparently falls back to the labeled synthetic seed data -
consistent with every other Module 3 connector's `(data, meta)`
contract, where `meta["status"]` is "success" | "fallback" | "error".
"""
import random
import threading

from config import Config
from core.logging_config import get_logger

logger = get_logger(__name__)

_ee_lock = threading.Lock()
_ee_ready = False
_ee_failed = False


def _ensure_ee_initialized() -> bool:
    """Lazily initializes the Earth Engine client exactly once per process."""
    global _ee_ready, _ee_failed
    if _ee_ready or _ee_failed:
        return _ee_ready

    with _ee_lock:
        if _ee_ready or _ee_failed:
            return _ee_ready

        try:
            import ee
        except ImportError as exc:
            logger.warning(
                "earthengine-api not installed (%s); CHIRPS will use fallback data. "
                "Install with `pip install earthengine-api`.", exc,
            )
            _ee_failed = True
            return False

        try:
            if Config.GEE_SERVICE_ACCOUNT_EMAIL and Config.GEE_SERVICE_ACCOUNT_KEY_FILE:
                credentials = ee.ServiceAccountCredentials(
                    Config.GEE_SERVICE_ACCOUNT_EMAIL, Config.GEE_SERVICE_ACCOUNT_KEY_FILE
                )
                ee.Initialize(credentials, project=Config.GEE_PROJECT_ID or None)
            elif Config.GEE_PROJECT_ID:
                ee.Initialize(project=Config.GEE_PROJECT_ID)
            else:
                ee.Initialize()  # relies on prior `earthengine authenticate` ADC
            _ee_ready = True
            logger.info("Google Earth Engine initialized for CHIRPS access.")
        except Exception as exc:  # noqa: BLE001 - broad at the auth boundary by design
            logger.warning(
                "Earth Engine initialization failed (%s); CHIRPS will use fallback data.", exc
            )
            _ee_failed = True

    return _ee_ready


class CHIRPSClient:
    """
    Google Earth Engine-backed CHIRPS connector.

    Note: unlike the REST-based connectors in this package, this client
    talks to Earth Engine's Python API rather than plain HTTP, so it
    does not subclass `BaseAPIClient` - but it preserves the identical
    `fetch_*(...) -> (data, meta)` calling convention used everywhere
    else in `api/`, so `services/data_service.py` and the UI don't need
    to know the transport differs.
    """

    source_name = "CHIRPS_GEE"
    COLLECTION_ID = "UCSB-CHG/CHIRPS/DAILY"
    NATIVE_SCALE_M = 5566  # ~0.05 degree native CHIRPS pixel size

    # ---------- point (county centroid) queries ----------

    def _live_fetch_point(self, lat, lon, start_date, end_date):
        import ee

        if not _ensure_ee_initialized():
            raise RuntimeError("Earth Engine is not initialized")

        point = ee.Geometry.Point([lon, lat])
        collection = (
            ee.ImageCollection(self.COLLECTION_ID)
            .filterDate(start_date, end_date)
            .filterBounds(point)
        )

        def _extract(image):
            value = image.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=self.NATIVE_SCALE_M
            ).get("precipitation")
            return image.set({
                "date": image.date().format("YYYY-MM-dd"),
                "precip": value,
            })

        features = collection.map(_extract)
        dates = features.aggregate_array("date").getInfo()
        precip = features.aggregate_array("precip").getInfo()

        daily = {
            d: round(p, 2) for d, p in zip(dates, precip) if p is not None
        }
        monthly = self._daily_to_monthly(daily)
        annual_total = round(sum(daily.values()), 1)

        return {
            "daily_mm": daily,
            "monthly_rainfall_mm": monthly,
            "annual_total_mm": annual_total,
            "source": f"Google Earth Engine - {self.COLLECTION_ID}",
        }

    def _fallback_point(self, lat, lon, start_date, end_date):
        rng = random.Random(int(abs(lat * 100) + abs(lon * 100)))
        monthly = {m: round(rng.uniform(10, 220), 1) for m in range(1, 13)}
        return {
            "monthly_rainfall_mm": monthly,
            "annual_total_mm": round(sum(monthly.values()), 1),
            "source": "synthetic seed (Earth Engine unavailable/unauthenticated)",
        }

    def fetch_rainfall(self, lat, lon, start_date="2025-01-01", end_date="2025-12-31"):
        """Point query: county-centroid daily/monthly/annual rainfall (mm)."""
        return self._safe_call(
            self._live_fetch_point, self._fallback_point, lat, lon, start_date, end_date
        )

    # ---------- region (county polygon) queries ----------

    def _live_fetch_region(self, geojson_geometry, start_date, end_date, reducer="sum"):
        import ee

        if not _ensure_ee_initialized():
            raise RuntimeError("Earth Engine is not initialized")

        geom = ee.Geometry(geojson_geometry)
        collection = (
            ee.ImageCollection(self.COLLECTION_ID)
            .filterDate(start_date, end_date)
            .filterBounds(geom)
        )

        ee_reducer = ee.Reducer.sum() if reducer == "sum" else ee.Reducer.mean()
        composite = collection.select("precipitation").reduce(ee_reducer)
        stats = composite.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=geom, scale=self.NATIVE_SCALE_M, maxPixels=1e9
        ).getInfo()

        value = next(iter(stats.values())) if stats else None
        return {
            "period_precipitation_mm": round(value, 1) if value is not None else None,
            "reducer": reducer,
            "source": f"Google Earth Engine - {self.COLLECTION_ID}",
        }

    def _fallback_region(self, geojson_geometry, start_date, end_date, reducer="sum"):
        rng = random.Random(hash(str(geojson_geometry)) % (2**32))
        return {
            "period_precipitation_mm": round(rng.uniform(200, 1800), 1),
            "reducer": reducer,
            "source": "synthetic seed (Earth Engine unavailable/unauthenticated)",
        }

    def fetch_rainfall_for_region(self, geojson_geometry, start_date="2025-01-01",
                                   end_date="2025-12-31", reducer="sum"):
        """
        Region query: aggregate CHIRPS precipitation over a county polygon
        (GeoJSON geometry dict) rather than a single point - the more
        GIS-appropriate query for choropleth/zonal-statistics use cases.
        """
        return self._safe_call(
            self._live_fetch_region, self._fallback_region,
            geojson_geometry, start_date, end_date, reducer,
        )

    # ---------- shared helpers ----------

    @staticmethod
    def _daily_to_monthly(daily: dict) -> dict:
        monthly = {}
        for date_str, value in daily.items():
            month = int(date_str.split("-")[1])
            monthly[month] = monthly.get(month, 0) + value
        return {k: round(v, 1) for k, v in sorted(monthly.items())}

    def _safe_call(self, live_fn, fallback_fn, *args, **kwargs):
        try:
            data = live_fn(*args, **kwargs)
            return data, {"status": "success", "source": self.source_name}
        except Exception as exc:  # noqa: BLE001 - deliberately broad at the boundary
            logger.warning("[%s] live fetch failed (%s); using fallback.", self.source_name, exc)
            if not Config.ALLOW_SYNTHETIC_FALLBACK:
                return None, {"status": "error", "source": self.source_name, "detail": str(exc)}
            data = fallback_fn(*args, **kwargs)
            return data, {"status": "fallback", "source": self.source_name, "detail": str(exc)}
