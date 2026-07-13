"""
components/scarcity_panel.py
"Water Scarcity" wireframe panel — choropleth of the water scarcity
index by county.
"""
import streamlit as st
import plotly.express as px
import json

from core.constants import PANEL_TITLES, COLOR_SCALE_SCARCITY, DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM
from config import Config


def render_scarcity_panel(df):
    st.subheader(PANEL_TITLES["scarcity"])

    with open(Config.COUNTY_GEOJSON) as f:
        geojson = json.load(f)

    fig = px.choropleth_mapbox(
        df, geojson=geojson, locations="county",
        featureidkey="properties.county",
        color="water_scarcity_index",
        color_continuous_scale=COLOR_SCALE_SCARCITY,
        range_color=(0, 1),
        mapbox_style="carto-positron",
        center=DEFAULT_MAP_CENTER, zoom=DEFAULT_MAP_ZOOM - 1,
        opacity=0.75,
        hover_data={"county": True, "water_scarcity_index": ":.2f"},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=340, coloraxis_colorbar_title="Scarcity")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("0 = abundant, 1 = severe scarcity (composite index).")
