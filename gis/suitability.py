"""
gis/suitability.py
Weighted-overlay multi-criteria suitability analysis for rainwater
harvesting potential, combining:
  - rainfall (higher is better)
  - existing water scarcity (higher scarcity -> higher need/suitability)
  - distance to water (further -> more suitable for local harvesting)
  - groundwater recharge (lower recharge -> harvesting more valuable)

All inputs are expected pre-normalized 0-1; weights sum to 1.0.
"""

DEFAULT_WEIGHTS = {
    "rainfall_norm": 0.35,
    "scarcity_norm": 0.30,
    "distance_norm": 0.20,
    "low_recharge_norm": 0.15,
}


def normalize(series):
    lo, hi = series.min(), series.max()
    if hi == lo:
        return series * 0
    return (series - lo) / (hi - lo)


def rainwater_harvesting_suitability(df, weights=None):
    """
    df: DataFrame with columns rainfall_mm_annual, water_scarcity_index,
        distance_to_water_km, groundwater_recharge_mm
    Returns a Series of suitability scores in [0, 1].
    """
    weights = weights or DEFAULT_WEIGHTS
    rainfall_norm = normalize(df["rainfall_mm_annual"])
    scarcity_norm = df["water_scarcity_index"]  # already 0-1
    distance_norm = normalize(df["distance_to_water_km"])
    low_recharge_norm = 1 - normalize(df["groundwater_recharge_mm"])

    score = (
        weights["rainfall_norm"] * rainfall_norm
        + weights["scarcity_norm"] * scarcity_norm
        + weights["distance_norm"] * distance_norm
        + weights["low_recharge_norm"] * low_recharge_norm
    )
    return score.clip(0, 1).round(3)
