"""
api/wra.py
Water Resources Authority (Kenya) connector. WRA does not currently
publish a stable public REST API, so this client is written against a
documented placeholder contract (`WRA_API_BASE_URL` + `WRA_API` key in
.env). Swap `_live_fetch`'s endpoint path for the real one once WRA
issues API credentials — the rest of the app (services/, components/)
depends only on the return shape below, not on WRA's wire format.
"""
import random

from api.base import BaseAPIClient
from config import Config

class WRAClient(BaseAPIClient):
    source_name = "WRA"

    def _live_fetch(self, county):
        headers = {"Authorization": f"Bearer {Config.WRA_API}"} if Config.WRA_API else None
        return self.get(f"{Config.WRA_API_BASE_URL}/boreholes", params={"county": county}, headers=headers)

    def _fallback(self, county):
        rng = random.Random(hash(county) % (2**32))
        n = rng.randint(15, 900)
        return {
            "county": county,
            "registered_boreholes": n,
            "permitted_abstraction_m3_year": round(n * rng.uniform(800, 5000), 0),
            "source": "synthetic seed (replace with live WRA feed)",
        }

    def fetch_borehole_registry(self, county):
        return self.safe_fetch(self._live_fetch, self._fallback, county)
