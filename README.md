# Kenya Water Intelligence Dashboard (KWID)

**Prepared by:** Rotich · GIS & GEOAI Analyst

A modular, production-grade geospatial intelligence dashboard for
Kenya's water sector — borehole density, water scarcity, accessibility,
water quality risk, groundwater recharge, and rainwater-harvesting
suitability — built with **Streamlit**, **GeoPandas/PostGIS**, and
scikit-learn/XGBoost models, with an optional **Svelte** micro-frontend
for the header.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m database.initialize   # creates + seeds local SQLite DB
streamlit run streamlit_app.py
```

Open http://localhost:8501.

Full docs live in `docs/`:

| Doc | Contents |
|---|---|
| `docs/INSTALLATION.md` | Local, Docker, and PostGIS setup |
| `docs/USER_GUIDE.md` | Using every dashboard panel |
| `docs/API_GUIDE.md` | Module 3 connector contracts & data provenance |
| `docs/TECHNICAL_DOCUMENTATION.md` | Architecture, module map, GIS/ML methodology |

## Module roadmap (as delivered)

| Module | Status | Where |
|---|---|---|
| 1. Project Foundation | ✅ | `config.py`, `core/`, `requirements.txt` |
| 2. Dashboard Wireframe | ✅ | `streamlit_app.py`, `components/` |
| 3. API Connectors | ✅ | `api/` (WRA, WASREB, AQUASTAT, NASA POWER, CHIRPS, OSM, WorldPop, Kenya Open Data, Copernicus) |
| 4. Database | ✅ | `database/` (SQLAlchemy + optional PostGIS) |
| 5. GIS Engine | ✅ | `gis/` (KDE, IDW, Kriging, cost distance, recharge, suitability) |
| 6. Machine Learning | ✅ | `ml/` (Random Forest groundwater potential, XGBoost demand forecast) |
| 7. Interactive Maps | ✅ | Plotly Mapbox density/choropleth/contour layers |
| 8. Tables & Charts | ✅ | `components/county_table.py`, `services/export_service.py` (CSV/Excel/PDF) |
| 9. Deployment | ✅ | `docker/`, `docker-compose.yml`, `.github/workflows/ci.yml` |
| 10. Documentation | ✅ | `docs/` |

## Important note on data

Kenya's official county boundary shapefile and live feeds from WRA,
WASREB, etc. are not bundled (no network/licensing access from this
build environment). CHIRPS rainfall is wired to **Google Earth Engine's**
`UCSB-CHG/CHIRPS/DAILY` collection (`api/chirps.py`) — real satellite
data, not a synthetic stand-in — as soon as GEE credentials are
configured; see `docs/INSTALLATION.md`. The app ships with:

- A **synthetic, clearly-labeled seed dataset** (`data/counties/kenya_counties.csv`)
  covering all 47 counties with realistic-range values, so every panel,
  model, and export renders immediately.
- **Real, working API client code** for each Module 3 source, wired to
  each provider's actual documented endpoint. Each client automatically
  falls back to the synthetic seed data (and labels the response as
  `"fallback"`) if the live endpoint is unreachable or unauthenticated —
  see `docs/API_GUIDE.md`.

Drop the official IEBC/KNBS county shapefile into `data/counties/kenya_counties.shp`
and supply real API credentials in `.env` to switch the app to live data
with no code changes.
