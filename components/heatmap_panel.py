"""
components/heatmap_panel.py
"Heat Map" wireframe panel — Kernel Density Estimation of borehole
density rendered as a Plotly Mapbox density layer (Module 5 + 7).
"""
import streamlit as st
import plotly.graph_objects as go

from gis.kde import borehole_kde
from core.constants import PANEL_TITLES, DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, COLOR_SCALE_DENSITY
from config import Config


def render_heatmap_panel(df):
    st.subheader(PANEL_TITLES["heatmap"])

    weights = (df["boreholes"].clip(lower=1)).tolist()
    lats, lons = [], []
    for _, row in df.iterrows():
        lats.extend([row["lat"]] * max(int(row["boreholes"] / 20), 1))
        lons.extend([row["lon"]] * max(int(row["boreholes"] / 20), 1))

    fig = go.Figure(go.Densitymapbox(
        lat=lats, lon=lons, radius=22,
        colorscale=COLOR_SCALE_DENSITY,
        showscale=True,
    ))
    fig.update_layout(
        mapbox=dict(
            style="carto-positron" if not Config.MAPBOX_TOKEN else "dark",
            accesstoken=Config.MAPBOX_TOKEN or None,
            center=DEFAULT_MAP_CENTER, zoom=DEFAULT_MAP_ZOOM,
        ),
        margin=dict(l=0, r=0, t=0, b=0), height=340,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Kernel Density Estimation over registered borehole locations (Module 5).")
