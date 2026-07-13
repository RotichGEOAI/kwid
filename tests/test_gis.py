import numpy as np
import pandas as pd

from gis.kde import borehole_kde
from gis.interpolation import idw
from gis.cost_distance import accessibility_score
from gis.groundwater import estimate_recharge_mm
from gis.suitability import rainwater_harvesting_suitability
from gis.utils import haversine_km


def test_haversine_zero_distance():
    assert haversine_km(-1.28, 36.8, -1.28, 36.8) == 0


def test_kde_normalized():
    lats = [-1.2, -1.3, -1.25, 0.5]
    lons = [36.8, 36.9, 36.85, 34.2]
    _, _, density = borehole_kde(lats, lons, grid_size=15)
    assert density.max() == 1.0
    assert density.min() >= 0


def test_idw_matches_input_at_sample_point():
    lats, lons, values = [0.0, 1.0], [0.0, 1.0], [10.0, 20.0]
    grid_lats = np.array([0.0])
    grid_lons = np.array([0.0])
    surface = idw(lats, lons, values, grid_lats, grid_lons)
    assert abs(surface[0, 0] - 10.0) < 0.5


def test_accessibility_score_bounds():
    assert accessibility_score(0) == 1.0
    assert accessibility_score(100, max_acceptable_km=5) == 0.0


def test_recharge_positive():
    assert estimate_recharge_mm(1000, "sandy") > 0


def test_suitability_range():
    df = pd.DataFrame({
        "rainfall_mm_annual": [200, 800, 1500],
        "water_scarcity_index": [0.2, 0.5, 0.9],
        "distance_to_water_km": [1, 5, 10],
        "groundwater_recharge_mm": [10, 50, 100],
    })
    scores = rainwater_harvesting_suitability(df)
    assert scores.between(0, 1).all()
