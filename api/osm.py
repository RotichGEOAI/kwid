"""
api/osm.py
OpenStreetMap Overpass API connector — pulls water-related infrastructure
(wells, water points, boreholes, springs) tagged in OSM for a bounding
box. Real, public, keyless endpoint.
Docs: https://wiki.openstreetmap.org/wiki/Overpass_API
"""
import random

from api.base import BaseAPIClient
from config import Config
from core.logging_config import get_logger

logger = get_logger(__name__)

OVERPASS_QUERY_TMPL = """
[out:json][timeout:25];
(
  node["man_made"="water_well"]({bbox});
  node["amenity"="water_point"]({bbox});
  node["natural"="spring"]({bbox});
);
out body;
"""


class OSMClient(BaseAPIClient):
    source_name = "OSM"

    def _live_fetch(self, south, west, north, east):
        bbox = f"{south},{west},{north},{east}"
        query = OVERPASS_QUERY_TMPL.format(bbox=bbox)
        resp = self.session.post(Config.OSM_OVERPASS_URL, data={"data": query}, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        elements = data.get("elements", [])
        return [
            {"lat": el["lat"], "lon": el["lon"], "tags": el.get("tags", {})}
            for el in elements if "lat" in el
        ]

    def _fallback(self, south, west, north, east):
        rng = random.Random(int((south + west) * 1000))
        n = rng.randint(5, 40)
        points = []
        for _ in range(n):
            points.append({
                "lat": rng.uniform(south, north),
                "lon": rng.uniform(west, east),
                "tags": {"man_made": rng.choice(["water_well", "water_point", "spring"])},
            })
        return points

    def fetch_water_points(self, south, west, north, east):
        return self.safe_fetch(self._live_fetch, self._fallback, south, west, north, east)
