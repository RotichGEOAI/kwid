# Technical Documentation

## Architecture

```
Streamlit UI (components/) 
        │
        ▼
services/  ── data_service.py (aggregation, caching) 
        │        export_service.py (CSV/Excel/PDF)
        ├──► database/  (SQLAlchemy ORM — SQLite dev / PostGIS prod)
        ├──► gis/       (KDE, IDW/Kriging, cost-distance, recharge, suitability)
        ├──► ml/        (RandomForest groundwater potential, XGBoost demand forecast)
        └──► api/       (WRA, WASREB, AQUASTAT, NASA POWER, CHIRPS (via Google
                          Earth Engine), OSM, WorldPop, Kenya Open Data,
                          Copernicus — each with live+fallback)
```

Design principle: **components/ never talks to database/, gis/, ml/ or
api/ directly** — everything routes through `services/`, so the data
strategy (live API vs. database vs. synthetic) can change without
touching UI code.

## Module-by-module notes

### Module 1 — Project Foundation
`config.py` is the single source of environment-driven settings
(`python-dotenv`). `core/logging_config.py` gives every module a
namespaced logger (`kwid.<module>`) writing to both stdout and a
rotating file (`logs/kwid.log`).

### Module 2 — Dashboard Wireframe
`streamlit_app.py` lays out the panels in the exact grid from the original
infographic (3-column map row → full-width table → 3-column risk row
→ full-width recommendations → footer). Each panel is an isolated
function in `components/`, independently testable/replaceable.

### Module 3 — API Connectors
See `docs/API_GUIDE.md`. Key design decision: **every external call is
wrapped in a live/fallback pair** so demo/offline environments and
production environments run the identical codepath.

### Module 4 — Database
SQLAlchemy models (`database/models.py`): `County`, `Borehole`,
`WaterStatistic`, `APIFetchLog`. Runs on SQLite with zero config;
setting `USE_POSTGIS=true` + a PostgreSQL `DATABASE_URL` swaps in
GeoAlchemy2 `Geometry` columns for the same models with no other code
changes. `psycopg2-binary` (the Postgres driver) lives in the base
`requirements.txt`, pinned `>=2.9.10` — that's the first release with
real Python 3.14 support and a published `cp314` wheel; the version
previously pinned here (`2.9.9`) predates 3.14 support entirely and
was the direct cause of a deployment failure when Streamlit Community
Cloud built against Python 3.14 (see `docs/INSTALLATION.md`).
`geoalchemy2` (only needed for PostGIS `Geometry` columns) stays in
`requirements-postgres.txt`; install both together when running
against real PostgreSQL:
`pip install -r requirements.txt -r requirements-postgres.txt`.
`database/models.py` raises a clear `ImportError` (rather than a bare
traceback) if `USE_POSTGIS=true` but `geoalchemy2` isn't installed.

### Module 5 — GIS Engine
- **KDE** (`gis/kde.py`): scikit-learn `KernelDensity` with a haversine
  metric so bandwidth is expressed in real kilometers rather than
  degrees.
- **IDW / Kriging** (`gis/interpolation.py`): custom vectorized IDW;
  `kriging()` uses `pykrige.OrdinaryKriging` when installed and
  transparently falls back to IDW otherwise (pykrige has a compiled
  dependency that isn't guaranteed in every deployment target).
- **Cost distance / accessibility** (`gis/cost_distance.py`): haversine
  nearest-point search plus an IDW-interpolated continuous
  accessibility surface, and a normalized 0–1 accessibility score.
- **Groundwater recharge** (`gis/groundwater.py`): transparent
  water-balance recharge-coefficient method (rainfall × soil-class
  coefficient), intentionally simple/auditable — contrast with the ML
  groundwater *potential* model in Module 6, which predicts yield.
- **Suitability** (`gis/suitability.py`): weighted-overlay multi-
  criteria analysis (rainfall, scarcity, distance, recharge) for
  rainwater-harvesting suitability, weights configurable via
  `DEFAULT_WEIGHTS`.

### Module 6 — Machine Learning
- **Groundwater potential** (`ml/groundwater_prediction.py`):
  `RandomForestRegressor` (300 trees) predicting borehole yield
  (m³/hr) from rainfall, recharge, distance-to-water, borehole
  density, and scarcity index.
- **Water demand forecast** (`ml/demand_forecast.py`): `XGBRegressor`
  predicting daily water demand (m³/day) from population, access %,
  scarcity, and borehole density, benchmarked against the WHO 40
  L/person/day minimum-basic standard.
- Both modules synthesize their training target from a transparent
  formula + noise in this demo build (`_synthesize_target`) — swap in
  real labeled data (metered consumption, borehole logs) for
  production and the rest of the pipeline is unaffected, since
  `services/data_service.py` only calls the public
  `predict_*`/`forecast_*` functions.
- Run `python -m ml.train` to retrain and print held-out MAE/R².

### Module 7 — Interactive Maps
Plotly `Densitymapbox` (heat map), `choropleth_mapbox` (scarcity), and
`Contour` (distance-to-water surface) — chosen over Dash/Leaflet for
native Streamlit compatibility (`st.plotly_chart`) without extra JS
bridging. `folium`/`streamlit-folium` are included in requirements for
teams that prefer a Leaflet-style alternative map layer.

### Module 8 — Tables & Charts
`components/county_table.py` provides sortable/filterable rankings;
`services/export_service.py` implements CSV, Excel (`openpyxl`), and
PDF (`reportlab`) export as in-memory byte buffers for
`st.download_button`, avoiding any server-side temp-file cleanup
concerns.

### Module 9 — Deployment
- `runtime.txt`: pins the Python version (`python-3.11`) for Streamlit
  Community Cloud, so pip resolves prebuilt wheels for every pinned
  package instead of falling back to a slow/fragile source build on
  whatever Python version the platform would otherwise default to.
- `docker/Dockerfile`: Python 3.11-slim + the app. No GDAL dev headers
  are installed — `geopandas` uses the `pyogrio` engine and
  `shapely`/`pyproj` ship self-contained wheels, so only `libpq-dev`
  (psycopg2) and `build-essential`/`curl` are needed.
- `docker-compose.yml`: app + PostGIS + nginx (WebSocket-aware reverse
  proxy — required because Streamlit's live session channel needs the
  `Upgrade`/`Connection` headers).
- `.github/workflows/ci.yml`: installs Python deps, runs `pytest`, and
  does an AST-parse smoke test of `streamlit_app.py`.

### Module 10 — Documentation
This file, plus `README.md`, `docs/USER_GUIDE.md`, and
`docs/API_GUIDE.md`, plus `docs/INSTALLATION.md`.

## Testing

`tests/` covers GIS engine correctness (KDE normalization, IDW exact
recovery at sample points, accessibility score bounds, recharge
positivity, suitability score range), API connector fallback
contracts, and ML prediction shape/sign checks. All 11 tests pass in
CI and were verified locally during this build (`pytest -q` → `11 passed`).

## Known simplifications (clearly labeled, safe to replace)

1. **County geometries** are simplified point-buffer squares
   (`data/counties/kenya_counties.geojson`), not the real IEBC/KNBS
   boundaries — swap in a real shapefile at
   `data/counties/kenya_counties.shp` (see `docs/INSTALLATION.md §4`).
2. **Seed statistics** (`data/counties/kenya_counties.csv`) are
   synthetic but realistic-range values seeded deterministically per
   county name — replace via the Module 3 live connectors once
   credentials/endpoints are available.
3. **ML training targets** are synthesized from transparent formulas
   for demo purposes (see Module 6 note above).
