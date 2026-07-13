"""
components/recommendations_panel.py
"Recommendations" wireframe panel — explainable priority ranking
combining scarcity, suitability, and existing infrastructure gaps.
"""
import streamlit as st

from core.constants import PANEL_TITLES
from services.data_service import generate_recommendations


def render_recommendations_panel(df):
    st.subheader(PANEL_TITLES["recommendations"])
    recs = generate_recommendations(df, top_n=5)
    st.dataframe(recs, use_container_width=True, height=220)
    st.caption(
        "Priority score = 0.45 × water scarcity + 0.35 × rainwater-harvesting "
        "suitability + 0.20 × (1 − relative borehole density). "
        "Weights are configurable in services/data_service.py."
    )


def render_footer():
    st.markdown("---")
    st.caption(
        "Kenya Water Intelligence Dashboard (KWID) · Prepared by Rotich, "
        "GIS & GEOAI Analyst · Data: WRA · WASREB · AQUASTAT · NASA POWER · "
        "CHIRPS · OpenStreetMap · WorldPop · Kenya Open Data · Copernicus"
    )
