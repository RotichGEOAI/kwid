"""
api/nasa_power.py
NASA POWER (Prediction Of Worldwide Energy Resources) daily point API.
Public, keyless REST API — real endpoint, used for rainfall/temperature
time series per county centroid.
Docs: https://power.larc.nasa.gov/docs/services/api/
"""
import random
from datetime import date, timedelta

from api.base import BaseAPIClient
from config import Config
from core.logging_config import get_logger

logger = get_logger(__name__)


class NASAPowerClient(BaseAPIClient):
    source_name = "NASA_POWER"

    PARAMETERS = "PRECTOTCORR,T2M,RH2M"  # precipitation, temp @2m, rel. humidity

    def _live_fetch(self, lat, lon, start, end):
        params = {
            "parameters": self.PARAMETERS,
            "community": "AG",
            "longitude": lon,
            "latitude": lat,
            "start": start,
            "end": end,
            "format": "JSON",
        }
        data = self.get(Config.NASA_POWER_BASE_URL, params=params, ttl=Config.__dict__.get("CACHE_TTL_SECONDS", 3600))
        props = data["properties"]["parameter"]
        return {
            "precipitation_mm": props.get("PRECTOTCORR", {}),
            "temp_c": props.get("T2M", {}),
            "humidity_pct": props.get("RH2M", {}),
        }

    def _fallback(self, lat, lon, start, end):
        rng = random.Random(int(abs(lat * 1000) + abs(lon * 1000)))
        d0 = date(int(start[:4]), int(start[4:6]), int(start[6:8]))
        d1 = date(int(end[:4]), int(end[4:6]), int(end[6:8]))
        days = (d1 - d0).days + 1
        precip, temp, hum = {}, {}, {}
        for i in range(max(days, 1)):
            d = (d0 + timedelta(days=i)).strftime("%Y%m%d")
            precip[d] = round(rng.uniform(0, 25), 2)
            temp[d] = round(rng.uniform(15, 32), 1)
            hum[d] = round(rng.uniform(30, 90), 1)
        return {"precipitation_mm": precip, "temp_c": temp, "humidity_pct": hum}

    def fetch_climate_point(self, lat, lon, start="20250101", end="20250131"):
        """Returns (data, meta). start/end format YYYYMMDD."""
        return self.safe_fetch(self._live_fetch, self._fallback, lat, lon, start, end)
