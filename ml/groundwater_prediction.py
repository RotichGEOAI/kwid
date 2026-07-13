"""
ml/groundwater_prediction.py
Random Forest regressor predicting groundwater potential (proxied here
by borehole yield, m3/hr) from county-level features. Trains on the
bundled seed dataset at import/first-use time and caches the fitted
model in-process; swap `load_training_data()` for a real labeled
dataset (borehole logs + geology + terrain) in production.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from core.logging_config import get_logger

logger = get_logger(__name__)

FEATURE_COLS = [
    "rainfall_mm_annual",
    "groundwater_recharge_mm",
    "distance_to_water_km",
    "borehole_density_per_km2",
    "water_scarcity_index",
]

_model_cache = {}


def _synthesize_target(df, rng):
    """
    Builds a plausible 'yield_m3_per_hr' target from features with noise,
    standing in for real borehole-log labels during local development.
    """
    base = (
        0.015 * df["rainfall_mm_annual"]
        + 0.08 * df["groundwater_recharge_mm"]
        - 0.6 * df["distance_to_water_km"]
        + 2.5 * (1 - df["water_scarcity_index"])
    )
    noise = rng.normal(0, 1.2, size=len(df))
    return np.clip(base + noise, 0.2, 20)


def train_model(df: pd.DataFrame, random_state=42):
    rng = np.random.default_rng(random_state)
    X = df[FEATURE_COLS].copy()
    y = _synthesize_target(df, rng)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

    model = RandomForestRegressor(n_estimators=300, max_depth=8, random_state=random_state, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "mae": round(mean_absolute_error(y_test, preds), 3),
        "r2": round(r2_score(y_test, preds), 3),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    logger.info("Groundwater RF model trained: %s", metrics)
    return model, metrics


def get_model(df: pd.DataFrame):
    if "model" not in _model_cache:
        model, metrics = train_model(df)
        _model_cache["model"] = model
        _model_cache["metrics"] = metrics
    return _model_cache["model"], _model_cache["metrics"]


def predict_groundwater_potential(df: pd.DataFrame) -> pd.Series:
    model, _ = get_model(df)
    preds = model.predict(df[FEATURE_COLS])
    return pd.Series(preds, index=df.index, name="predicted_yield_m3_per_hr").round(2)
