"""
components/risks_panel.py
"Risks" wireframe panel — flags counties combining high scarcity with
high water-quality risk (compound-risk view).
"""
import streamlit as st

from core.constants import PANEL_TITLES


def render_risks_panel(df):
    st.subheader(PANEL_TITLES["risks"])
    compound = df[(df["scarcity_band"] == "High") & (df["risk_band"] == "High")]
    if compound.empty:
        st.info("No counties currently flag both high scarcity and high water-quality risk.")
    else:
        st.warning(f"{len(compound)} counties show compound risk (high scarcity + high water-quality risk):")
        st.dataframe(
            compound[["county", "water_scarcity_index", "water_quality_risk_index"]]
            .sort_values("water_scarcity_index", ascending=False)
            .reset_index(drop=True),
            use_container_width=True, height=180,
        )
