"""
gis/utils.py
Small shared geospatial helpers (haversine distance, bounding boxes)
used by several GIS-engine and API-connector modules.
"""
import math


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def kenya_bbox():
    """Approximate national bounding box (south, west, north, east)."""
    return (-4.9, 33.9, 5.1, 41.9)


def county_bbox(lat, lon, pad_deg=0.6):
    return (lat - pad_deg, lon - pad_deg, lat + pad_deg, lon + pad_deg)
