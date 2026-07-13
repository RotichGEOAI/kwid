"""
ml/demand_forecast.py
XGBoost regressor forecasting per-county water demand (m3/day) from
population, scarcity, and access indicators. As with the groundwater
model, the training target is synthesized from a transparent formula
plus noise for demo purposes — replace `_synthesize_target` with real
consumption metering data in production.
"""
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from core.logging_config import get_logger

logger = get_logger(__name__)

FEATURE_COLS = [
    "population",
    "improved_water_access_pct",
    "water_scarcity_index",
    "borehole_density_per_km2",
]

PER_CAPITA_LPD = 40  # liters per person per day, WHO minimum-basic benchmark

_model_cache = {}


def _synthesize_target(df, rng):
    base_demand_m3 = df["population"] * PER_CAPITA_LPD / 1000.0
    access_penalty = 1 + (1 - df["improved_water_access_pct"] / 100.0) * 0.4
    scarcity_penalty = 1 + df["water_scarcity_index"] * 0.25
    noise = rng.normal(1.0, 0.05, size=len(df))
    return base_demand_m3 * access_penalty * scarcity_penalty * noise


def train_model(df: pd.DataFrame, random_state=42):
    rng = np.random.default_rng(random_state)
    X = df[FEATURE_COLS].copy()
    y = _synthesize_target(df, rng)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

    model = XGBRegressor(
        n_estimators=250, max_depth=5, learning_rate=0.06,
        subsample=0.9, colsample_bytree=0.9, random_state=random_state,
        objective="reg:squarederror",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "mae_m3_per_day": round(mean_absolute_error(y_test, preds), 1),
        "r2": round(r2_score(y_test, preds), 3),
    }
    logger.info("Water demand XGBoost model trained: %s", metrics)
    return model, metrics


def get_model(df: pd.DataFrame):
    if "model" not in _model_cache:
        model, metrics = train_model(df)
        _model_cache["model"] = model
        _model_cache["metrics"] = metrics
    return _model_cache["model"], _model_cache["metrics"]


def forecast_demand_m3_per_day(df: pd.DataFrame) -> pd.Series:
    model, _ = get_model(df)
    preds = model.predict(df[FEATURE_COLS])
    return pd.Series(preds, index=df.index, name="forecast_demand_m3_per_day").round(1)
