"""
api/copernicus.py
Copernicus Climate Data Store (CDS) connector — used for satellite-
derived soil moisture / land surface data feeding the groundwater
recharge and suitability models. Requires a free CDS API key
(COPERNICUS_API_KEY) in production; falls back to synthetic soil
moisture indices otherwise.
Docs: https://cds.climate.copernicus.eu/how-to-api
"""
import random

from api.base import BaseAPIClient
from config import Config

class CopernicusClient(BaseAPIClient):
    source_name = "COPERNICUS"

    def _live_fetch(self, lat, lon):
        headers = {"PRIVATE-TOKEN": Config.COPERNICUS_API_KEY} if Config.COPERNICUS_API_KEY else None
        return self.get(f"{Config.COPERNICUS_BASE_URL}/soil-moisture", params={"lat": lat, "lon": lon}, headers=headers)

    def _fallback(self, lat, lon):
        rng = random.Random(int(abs(lat * 500) + abs(lon * 500)))
        return {
            "lat": lat, "lon": lon,
            "soil_moisture_index": round(rng.uniform(0.05, 0.55), 3),
            "source": "synthetic seed (replace with CDS ERA5-Land soil moisture query)",
        }

    def fetch_soil_moisture(self, lat, lon):
        return self.safe_fetch(self._live_fetch, self._fallback, lat, lon)
