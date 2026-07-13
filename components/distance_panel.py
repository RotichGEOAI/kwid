"""
components/distance_panel.py
"Distance to Water" wireframe panel — accessibility surface built from
the cost-distance module (Module 5).
"""
import streamlit as st
import plotly.graph_objects as go

from gis.interpolation import idw
import numpy as np

from core.constants import PANEL_TITLES, DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM
from config import Config


def render_distance_panel(df):
    st.subheader(PANEL_TITLES["distance"])

    grid_lats = np.linspace(df["lat"].min() - 1, df["lat"].max() + 1, 40)
    grid_lons = np.linspace(df["lon"].min() - 1, df["lon"].max() + 1, 40)
    surface = idw(df["lat"], df["lon"], df["distance_to_water_km"], grid_lats, grid_lons)

    fig = go.Figure(go.Contour(
        z=surface, x=grid_lons, y=grid_lats,
        colorscale="Turbo", colorbar=dict(title="km"),
        contours=dict(showlabels=True),
    ))
    fig.add_trace(go.Scatter(
        x=df["lon"], y=df["lat"], mode="markers+text",
        marker=dict(size=4, color="black"),
        text=df["county"], textposition="top center", textfont=dict(size=7),
        showlegend=False,
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=340,
                       xaxis_title="Longitude", yaxis_title="Latitude")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("IDW-interpolated distance-to-nearest-water-point surface (km).")
