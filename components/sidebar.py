"""
components/sidebar.py
Global filters (county, scarcity band) shared across all panels, plus
data-provenance indicators for the API connectors (Module 3).
"""
import streamlit as st


def render_sidebar(df):
    st.sidebar.title("KWID Controls")
    counties = ["All Counties"] + sorted(df["county"].unique().tolist())
    selected_county = st.sidebar.selectbox("County", counties)

    scarcity_bands = ["All"] + sorted(df["scarcity_band"].unique().tolist())
    selected_band = st.sidebar.selectbox("Water Scarcity Band", scarcity_bands)

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Data provenance: live API results are cached for up to 1 hour; "
        "when a source is unreachable the panel falls back to the bundled "
        "synthetic seed dataset and is labeled accordingly."
    )

    filtered = df.copy()
    if selected_county != "All Counties":
        filtered = filtered[filtered["county"] == selected_county]
    if selected_band != "All":
        filtered = filtered[filtered["scarcity_band"] == selected_band]

    return filtered, selected_county
