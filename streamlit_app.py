"""
streamlit_app.py
Entry point for the Kenya Water Intelligence Dashboard (KWID).

Layout mirrors the original infographic wireframe exactly:

    --------------------------------------------------------------
    HEADER
    Kenya Borehole Density, Water Scarcity & The Way Forward
    Rotich | GIS & GEOAI Analyst
    --------------------------------------------------------------
    Heat Map        |   Water Scarcity   |   Distance to Water
    --------------------------------------------------------------
    County Statistics Table
    --------------------------------------------------------------
    Water Quality   |   Risks            |   Rainwater Harvesting
    --------------------------------------------------------------
    Recommendations
    Footer

Run with:   streamlit run streamlit_app.py
"""
import streamlit as st

from config import Config
from database.initialize import initialize as init_db
from services.data_service import get_county_dataframe, national_summary
from components.header import render_header
from components.sidebar import render_sidebar
from components.heatmap_panel import render_heatmap_panel
from components.scarcity_panel import render_scarcity_panel
from components.distance_panel import render_distance_panel
from components.county_table import render_county_table
from components.water_quality_panel import render_water_quality_panel
from components.risks_panel import render_risks_panel
from components.rainwater_panel import render_rainwater_panel
from components.recommendations_panel import render_recommendations_panel, render_footer

st.set_page_config(
    page_title=Config.APP_NAME, page_icon="💧", layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def _bootstrap_database():
    init_db()
    return True


def main():
    _bootstrap_database()
    render_header()

    df_all = get_county_dataframe()
    df, selected_county = render_sidebar(df_all)

    summary = national_summary(df_all)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Counties", summary["counties"])
    m2.metric("Total Boreholes", f"{summary['total_boreholes']:,}")
    m3.metric("Avg. Distance to Water", f"{summary['avg_distance_to_water_km']} km")
    m4.metric("High-Scarcity Counties", summary["high_scarcity_counties"])
    m5.metric("Forecast Demand", f"{summary['total_forecast_demand_m3_day']:,.0f} m³/day")

    st.markdown("---")

    row1 = st.columns(3)
    with row1[0]:
        render_heatmap_panel(df)
    with row1[1]:
        render_scarcity_panel(df)
    with row1[2]:
        render_distance_panel(df)

    st.markdown("---")
    render_county_table(df)

    st.markdown("---")
    row2 = st.columns(3)
    with row2[0]:
        render_water_quality_panel(df)
    with row2[1]:
        render_risks_panel(df)
    with row2[2]:
        render_rainwater_panel(df)

    st.markdown("---")
    render_recommendations_panel(df)
    render_footer()


if __name__ == "__main__":
    main()
