"""
api/wasreb.py
Water Services Regulatory Board (WASREB) connector. WASREB publishes an
annual "Impact Report" with utility-level performance (non-revenue
water, coverage, tariffs) rather than a live API, so this client
targets a configurable data endpoint (`WASREB_API_BASE_URL`) and falls
back to synthetic utility performance indicators keyed by county.
"""
import random

from api.base import BaseAPIClient
from config import Config

class WASREBClient(BaseAPIClient):
    source_name = "WASREB"

    def _live_fetch(self, county):
        headers = {"Authorization": f"Bearer {Config.WASREB_API}"} if Config.WASREB_API else None
        return self.get(f"{Config.WASREB_API_BASE_URL}/utilities", params={"county": county}, headers=headers)

    def _fallback(self, county):
        rng = random.Random(hash(("wasreb", county)) % (2**32))
        return {
            "county": county,
            "water_coverage_pct": round(rng.uniform(25, 92), 1),
            "non_revenue_water_pct": round(rng.uniform(18, 55), 1),
            "avg_tariff_kes_per_m3": round(rng.uniform(35, 120), 2),
            "source": "synthetic seed (replace with WASREB Impact Report feed)",
        }

    def fetch_utility_performance(self, county):
        return self.safe_fetch(self._live_fetch, self._fallback, county)
