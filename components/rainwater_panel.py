"""
components/rainwater_panel.py
"Rainwater Harvesting" wireframe panel — suitability ranking (Module 5
weighted-overlay suitability analysis).
"""
import streamlit as st
import plotly.express as px

from core.constants import PANEL_TITLES, COLOR_SCALE_SUITABILITY


def render_rainwater_panel(df):
    st.subheader(PANEL_TITLES["rainwater"])
    top = df.sort_values("rainwater_harvesting_suitability_calc", ascending=False).head(15)
    fig = px.bar(
        top, x="rainwater_harvesting_suitability_calc", y="county", orientation="h",
        color="rainwater_harvesting_suitability_calc", color_continuous_scale=COLOR_SCALE_SUITABILITY,
        labels={"rainwater_harvesting_suitability_calc": "Suitability Score", "county": ""},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=340, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
