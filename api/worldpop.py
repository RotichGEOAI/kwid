"""
api/worldpop.py
WorldPop REST API connector — gridded population estimates, used to
compute per-capita water access & demand. Real public endpoint.
Docs: https://www.worldpop.org/sdi/introapi
"""
import random

from api.base import BaseAPIClient
from config import Config

class WorldPopClient(BaseAPIClient):
    source_name = "WORLDPOP"

    def _live_fetch(self, iso3="KEN", year=2024):
        return self.get(f"{Config.WORLDPOP_BASE_URL}/pop/wpgppop", params={"iso3": iso3, "year": year})

    def _fallback(self, iso3="KEN", year=2024):
        rng = random.Random(year)
        return {
            "iso3": iso3, "year": year,
            "estimated_total_population": 55_100_000 + rng.randint(-200_000, 200_000),
            "source": "synthetic seed (replace with live WorldPop grid query)",
        }

    def fetch_population_estimate(self, iso3="KEN", year=2024):
        return self.safe_fetch(self._live_fetch, self._fallback, iso3, year)
