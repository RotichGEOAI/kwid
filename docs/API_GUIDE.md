# API Guide — Module 3 Connectors

Every REST-based connector in `api/` inherits `BaseAPIClient`
(`api/base.py`), which provides:

- Retry with exponential backoff (429/500/502/503/504)
- A 1-hour on-disk JSON response cache (`data/raw/_api_cache/`)
- A uniform **`safe_fetch(fetch_fn, fallback_fn, ...)`** wrapper returning
  `(data, meta)`, where `meta["status"]` is one of:
  - `"success"` — live API call succeeded
  - `"fallback"` — live call failed/unavailable; synthetic seed data returned instead
  - `"error"` — call failed and `ALLOW_SYNTHETIC_FALLBACK=false`

`CHIRPSClient` is the one exception: it talks to Google Earth Engine's
Python API rather than plain HTTP, so it doesn't subclass
`BaseAPIClient`, but it implements the identical
`fetch_*(...) -> (data, meta)` contract (see the dedicated section
below) so calling code is none the wiser.

This means **no panel ever crashes** because a third-party API/service
is down or unauthenticated — it degrades to labeled synthetic data
instead.

## Connectors

| Client | File | Real endpoint | Auth |
|---|---|---|---|
| `WRAClient` | `api/wra.py` | Configurable (`WRA_API_BASE_URL`) — WRA has no stable public REST API at time of writing | Bearer token (`WRA_API`) |
| `WASREBClient` | `api/wasreb.py` | Configurable (`WASREB_API_BASE_URL`) | Bearer token (`WASREB_API`) |
| `AquastatClient` | `api/aquastat.py` | `https://data.apps.fao.org/aquastat/api/v1` | None (public) |
| `NASAPowerClient` | `api/nasa_power.py` | `https://power.larc.nasa.gov/api/temporal/daily/point` | None (public, keyless) |
| `CHIRPSClient` | `api/chirps.py` | Google Earth Engine `UCSB-CHG/CHIRPS/DAILY` ImageCollection | GEE service-account or user credentials |
| `OSMClient` | `api/osm.py` | `https://overpass-api.de/api/interpreter` | None (public) |
| `WorldPopClient` | `api/worldpop.py` | `https://www.worldpop.org/rest/data` | None (public) |
| `KenyaOpenDataClient` | `api/kenya_open_data.py` | Configurable | None |
| `CopernicusClient` | `api/copernicus.py` | `https://cds.climate.copernicus.eu/api/v2` | API key (`COPERNICUS_API_KEY`) |

## CHIRPS via Google Earth Engine

`CHIRPSClient` (`api/chirps.py`) is the one connector that does **not**
speak plain REST — it queries Google Earth Engine's
`UCSB-CHG/CHIRPS/DAILY` ImageCollection server-side, giving actual
GEOAI-grade zonal statistics rather than a third-party API wrapper.

**Auth** — set one of these in `.env`:

```bash
# Option 1: service account (servers / CI / Docker)
GEE_SERVICE_ACCOUNT_EMAIL=my-sa@my-project.iam.gserviceaccount.com
GEE_SERVICE_ACCOUNT_KEY_FILE=/secure/path/to/key.json
GEE_PROJECT_ID=my-gcp-project

# Option 2: user/local dev — run `earthengine authenticate` once, then:
GEE_PROJECT_ID=my-gcp-project
```

**Point query** (county centroid):

```python
from api.chirps import CHIRPSClient

client = CHIRPSClient()
data, meta = client.fetch_rainfall(lat=-1.28, lon=36.82, start_date="2025-01-01", end_date="2025-12-31")
# data: {"daily_mm": {...}, "monthly_rainfall_mm": {1: ..., ..., 12: ...},
#        "annual_total_mm": ..., "source": "Google Earth Engine - UCSB-CHG/CHIRPS/DAILY"}
```

**Region query** (county polygon — proper zonal statistics):

```python
data, meta = client.fetch_rainfall_for_region(
    geojson_geometry=county_polygon,   # a GeoJSON Polygon/MultiPolygon dict
    start_date="2025-01-01", end_date="2025-12-31", reducer="sum",
)
# data: {"period_precipitation_mm": ..., "reducer": "sum", "source": "..."}
```

If `earthengine-api` isn't installed, credentials aren't configured, or
the call fails (quota/connectivity), both methods fall back to the
labeled synthetic seed rainfall data — `meta["status"]` will read
`"fallback"` and `data["source"]` will say so explicitly, so the UI can
show provenance rather than silently mixing real and synthetic values.

## Example usage

```python
from api.nasa_power import NASAPowerClient

client = NASAPowerClient()
data, meta = client.fetch_climate_point(lat=-1.28, lon=36.82, start="20250101", end="20250131")

if meta["status"] == "fallback":
    print("Using synthetic data:", meta["detail"])

print(data["precipitation_mm"])
```

## Adding a new connector

1. Create `api/<source>.py` subclassing `BaseAPIClient`.
2. Implement `_live_fetch(...)` (raises on failure) and `_fallback(...)`
   (never raises — returns a plausible synthetic payload with `"source"` labeled).
3. Expose a public `fetch_<thing>(...)` method calling
   `self.safe_fetch(self._live_fetch, self._fallback, ...)`.
4. Consume it from `services/data_service.py`, never directly from `components/`.
