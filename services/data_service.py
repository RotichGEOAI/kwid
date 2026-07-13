"""
services/data_service.py
The seam between raw sources (database, GIS engine, API connectors, ML
models) and the UI (components/). Every component should call into
this module rather than touching database/gis/api/ml directly, so the
data-access strategy can change in one place.
"""
import pandas as pd
import streamlit as st

from gis.county_loader import load_counties_dataframe
from gis.suitability import rainwater_harvesting_suitability
from gis.groundwater import estimate_recharge_mm
from gis.cost_distance import accessibility_score
from ml.groundwater_prediction import predict_groundwater_potential
from ml.demand_forecast import forecast_demand_m3_per_day
from core.constants import RISK_THRESHOLDS, SCARCITY_THRESHOLDS
from core.logging_config import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=3600, show_spinner=False)
def get_county_dataframe() -> pd.DataFrame:
    """Single cached source of truth for the whole dashboard session."""
    df = load_counties_dataframe()

    df["rainwater_harvesting_suitability_calc"] = rainwater_harvesting_suitability(df)
    df["accessibility_score"] = df["distance_to_water_km"].apply(accessibility_score)

    df["predicted_yield_m3_per_hr"] = predict_groundwater_potential(df)
    df["forecast_demand_m3_per_day"] = forecast_demand_m3_per_day(df)

    df["scarcity_band"] = df["water_scarcity_index"].apply(lambda v: _band(v, SCARCITY_THRESHOLDS))
    df["risk_band"] = df["water_quality_risk_index"].apply(lambda v: _band(v, RISK_THRESHOLDS))

    return df


def _band(value, thresholds):
    if value <= thresholds["low"]:
        return "Low"
    if value <= thresholds["moderate"]:
        return "Moderate"
    return "High"


def national_summary(df: pd.DataFrame) -> dict:
    return {
        "counties": len(df),
        "total_boreholes": int(df["boreholes"].sum()),
        "avg_borehole_density": round(df["borehole_density_per_km2"].mean(), 3),
        "avg_distance_to_water_km": round(df["distance_to_water_km"].mean(), 2),
        "avg_scarcity_index": round(df["water_scarcity_index"].mean(), 3),
        "high_scarcity_counties": int((df["scarcity_band"] == "High").sum()),
        "high_risk_counties": int((df["risk_band"] == "High").sum()),
        "total_forecast_demand_m3_day": round(df["forecast_demand_m3_per_day"].sum(), 0),
    }


def generate_recommendations(df: pd.DataFrame, top_n=5) -> pd.DataFrame:
    """
    Simple, explainable prioritization: counties with high scarcity AND
    high rainwater-harvesting suitability AND low current borehole
    density are flagged as top intervention candidates.
    """
    priority = (
        df["water_scarcity_index"] * 0.45
        + df["rainwater_harvesting_suitability_calc"] * 0.35
        + (1 - df["borehole_density_per_km2"] / df["borehole_density_per_km2"].max()) * 0.20
    )
    out = df.assign(priority_score=priority.round(3)).sort_values("priority_score", ascending=False)
    cols = [
        "county", "priority_score", "water_scarcity_index",
        "rainwater_harvesting_suitability_calc", "borehole_density_per_km2",
        "distance_to_water_km", "forecast_demand_m3_per_day",
    ]
    return out[cols].head(top_n).reset_index(drop=True)
