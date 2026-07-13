"""
components/county_table.py
"County Statistics Table" wireframe panel — Module 8 interactive
rankings with CSV/Excel/PDF export.
"""
import streamlit as st

from core.constants import PANEL_TITLES
from services.export_service import to_csv_bytes, to_excel_bytes, to_pdf_bytes


DISPLAY_COLS = [
    "county", "population", "boreholes", "borehole_density_per_km2",
    "distance_to_water_km", "water_scarcity_index", "water_quality_risk_index",
    "rainfall_mm_annual", "groundwater_recharge_mm",
    "rainwater_harvesting_suitability_calc", "predicted_yield_m3_per_hr",
    "forecast_demand_m3_per_day", "scarcity_band", "risk_band",
]


def render_county_table(df):
    st.subheader(PANEL_TITLES["county_table"])

    sort_col = st.selectbox("Sort by", DISPLAY_COLS, index=DISPLAY_COLS.index("water_scarcity_index"))
    ascending = st.checkbox("Ascending", value=False)

    table_df = df[DISPLAY_COLS].sort_values(sort_col, ascending=ascending).reset_index(drop=True)
    st.dataframe(table_df, use_container_width=True, height=360)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Export CSV", to_csv_bytes(table_df), "kwid_county_statistics.csv", "text/csv")
    with c2:
        st.download_button(
            "Export Excel", to_excel_bytes(table_df), "kwid_county_statistics.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with c3:
        if st.button("Generate PDF Report"):
            pdf_bytes = to_pdf_bytes(table_df)
            st.download_button("Download PDF", pdf_bytes, "kwid_county_statistics.pdf", "application/pdf")
