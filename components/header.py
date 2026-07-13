"""
components/header.py
HEADER panel — mirrors the wireframe:
  Kenya Borehole Density, Water Scarcity & The Way Forward
  Rotich | GIS & GEOAI Analyst

If a compiled Svelte micro-frontend bundle exists (frontend/dist), it
is embedded for a richer animated header; otherwise pure Streamlit
markup is rendered so the app never hard-depends on a Node build step.
"""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from config import Config


def render_header():
    bundle = Config.SVELTE_BUILD_DIR / "index.html"
    if bundle.exists():
        components.html(bundle.read_text(), height=140, scrolling=False)
        return

    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#0B5394,#1C7ED6);
                    padding:1.1rem 1.6rem;border-radius:10px;margin-bottom:0.8rem;">
            <h1 style="color:white;margin:0;font-size:1.7rem;">
                Kenya Borehole Density, Water Scarcity &amp; The Way Forward
            </h1>
            <p style="color:#DCEBFB;margin:0.2rem 0 0 0;font-size:0.95rem;">
                {Config.AUTHOR} &nbsp;|&nbsp; {Config.AUTHOR_TITLE}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
