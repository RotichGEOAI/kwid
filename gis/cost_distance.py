"""
gis/cost_distance.py
Cost-distance / accessibility surface: estimates travel effort to the
nearest water point, optionally weighted by a friction surface (e.g.
slope, road network). This lightweight implementation treats each
county centroid's `distance_to_water_km` as the observed cost and
interpolates a continuous accessibility surface with IDW, plus a
straight haversine nearest-point calculator for point-level queries.
"""
import numpy as np

from gis.interpolation import idw
from gis.utils import haversine_km


def nearest_water_point_km(lat, lon, water_points):
    """water_points: iterable of (lat, lon). Returns distance in km to nearest."""
    dists = [haversine_km(lat, lon, wp_lat, wp_lon) for wp_lat, wp_lon in water_points]
    return min(dists) if dists else float("inf")


def accessibility_surface(lats, lons, distance_km_values, grid_lats, grid_lons):
    """Interpolated 'distance to water' continuous surface for the map panel."""
    return idw(lats, lons, distance_km_values, grid_lats, grid_lons, power=2)


def accessibility_score(distance_km, max_acceptable_km=5.0):
    """
    Normalizes raw distance into a 0 (poor) - 1 (excellent) accessibility
    score, used by the suitability/recommendation engine.
    """
    score = 1 - min(distance_km / max_acceptable_km, 1.0)
    return round(max(score, 0.0), 3)
