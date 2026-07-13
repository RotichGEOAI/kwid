"""
api/kenya_open_data.py
Kenya Open Data Portal connector (Socrata / OpenDataForAfrica backed).
Used for county-level socioeconomic indicators that complement the
water statistics (e.g. poverty index, literacy) for the recommendations
engine.
"""
import random

from api.base import BaseAPIClient
from config import Config

class KenyaOpenDataClient(BaseAPIClient):
    source_name = "KENYA_OPEN_DATA"

    def _live_fetch(self, county):
        return self.get(f"{Config.KENYA_OPEN_DATA_BASE_URL}/county-indicators", params={"county": county})

    def _fallback(self, county):
        rng = random.Random(hash(("kod", county)) % (2**32))
        return {
            "county": county,
            "poverty_rate_pct": round(rng.uniform(8, 65), 1),
            "literacy_rate_pct": round(rng.uniform(55, 96), 1),
            "source": "synthetic seed (replace with Kenya Open Data feed)",
        }

    def fetch_county_indicators(self, county):
        return self.safe_fetch(self._live_fetch, self._fallback, county)
