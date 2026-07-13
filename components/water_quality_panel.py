"""
components/water_quality_panel.py
"Water Quality" wireframe panel.
"""
import streamlit as st
import plotly.express as px

from core.constants import PANEL_TITLES, COLOR_SCALE_RISK


def render_water_quality_panel(df):
    st.subheader(PANEL_TITLES["water_quality"])
    top = df.sort_values("water_quality_risk_index", ascending=False).head(15)
    fig = px.bar(
        top, x="water_quality_risk_index", y="county", orientation="h",
        color="water_quality_risk_index", color_continuous_scale=COLOR_SCALE_RISK,
        labels={"water_quality_risk_index": "Risk Index", "county": ""},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=340, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
