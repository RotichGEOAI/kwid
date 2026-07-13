"""
api/aquastat.py
FAO AQUASTAT connector — national-level water resource statistics
(renewable water resources, withdrawal by sector). Real public API
base URL is configurable via AQUASTAT_BASE_URL.
Docs: https://data.apps.fao.org/aquastat/
"""
import random

from api.base import BaseAPIClient
from config import Config

class AquastatClient(BaseAPIClient):
    source_name = "AQUASTAT"

    def _live_fetch(self, country_code="KEN"):
        return self.get(f"{Config.AQUASTAT_BASE_URL}/data", params={"area": country_code})

    def _fallback(self, country_code="KEN"):
        return {
            "country": country_code,
            "total_renewable_water_resources_bcm": 30.7,
            "agricultural_withdrawal_pct": 58.0,
            "municipal_withdrawal_pct": 32.0,
            "industrial_withdrawal_pct": 10.0,
            "source": "synthetic seed approximating published AQUASTAT KEN figures",
        }

    def fetch_national_water_balance(self, country_code="KEN"):
        return self.safe_fetch(self._live_fetch, self._fallback, country_code)
