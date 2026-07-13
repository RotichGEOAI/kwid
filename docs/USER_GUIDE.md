# User Guide

## Layout

The dashboard mirrors the original infographic wireframe:

```
HEADER
Kenya Borehole Density, Water Scarcity & The Way Forward
------------------------------------------------------------------
Heat Map        |  Water Scarcity     |  Distance to Water
------------------------------------------------------------------
County Statistics Table
------------------------------------------------------------------
Water Quality   |  Risks              |  Rainwater Harvesting
------------------------------------------------------------------
Recommendations
Footer
```

## Sidebar controls

- **County** — filter every panel and the table to a single county, or view all 47.
- **Water Scarcity Band** — filter to Low / Moderate / High scarcity counties.
- Data-provenance note explaining the live/fallback caching behaviour.

## Panels

- **Heat Map** — Kernel Density Estimation of registered borehole locations.
- **Water Scarcity** — choropleth of the composite scarcity index (0 = abundant, 1 = severe).
- **Distance to Water** — IDW-interpolated accessibility surface (km to nearest water point), with county labels.
- **County Statistics Table** — sortable table of every metric per county; export to **CSV**, **Excel**, or a formatted **PDF report** via the buttons beneath the table.
- **Water Quality** — top 15 counties by water-quality risk index.
- **Risks** — counties flagged for *compound risk* (high scarcity **and** high water-quality risk simultaneously).
- **Rainwater Harvesting** — top 15 counties by rainwater-harvesting suitability score (weighted-overlay analysis).
- **Recommendations** — top 5 priority counties for intervention, with an explainable priority-score formula shown beneath the table.

## Top metric strip

Five headline KPIs above the panels: county count, total registered
boreholes, average distance to water, number of high-scarcity
counties, and total forecast daily water demand (from the XGBoost
demand model).

## Exporting data

Use the three buttons under the County Statistics Table:
1. **Export CSV** — immediate download.
2. **Export Excel** — formatted `.xlsx` workbook.
3. **Generate PDF Report** — click once to render, then use the
   download button that appears.
