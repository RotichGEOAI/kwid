# Installation Manual

## 1. Local development (SQLite, no Docker)

**Requirements:** Python 3.11 (pinned via `runtime.txt` for Streamlit
Community Cloud — see the deployment note below). No system GDAL
libraries are required: `geopandas` uses the `pyogrio` engine and
`shapely`/`pyproj` ship self-contained wheels.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # defaults work out-of-the-box
python -m database.initialize # creates data/processed/kwid.db and seeds 47 counties
streamlit run streamlit_app.py
```

Visit http://localhost:8501.

### Deploying to Streamlit Community Cloud

`runtime.txt` (`python-3.11`) is included, but **be aware of a current
platform bug**: Community Cloud has been observed silently ignoring
`runtime.txt` and building with a much newer Python (3.14 at time of
writing) regardless of what it specifies — see
[streamlit/streamlit#15326](https://github.com/streamlit/streamlit/issues/15326).
This is why an exact-pinned `requirements.txt` previously broke
deployment: `psycopg2-binary==2.9.9` and `pandas==2.2.2` had no
prebuilt wheel for that newer Python and fell back to a slow/fragile
source build (and for `psycopg2-binary`, that source build also needs
a system `pg_config`/`libpq` that Community Cloud's build image
doesn't provide, so it failed outright rather than just being slow).

The fix has two parts:

1. **`requirements.txt` now uses `>=` floors, not exact `==` pins**, so
   the resolver can pick whatever compatible release already has a
   wheel for whichever Python Community Cloud actually runs.
2. **`psycopg2-binary` is pinned to `>=2.9.10` specifically** — that's
   the first release with real Python 3.14 support; `2.9.12`+ publishes
   actual prebuilt wheels for `cp314` (including
   `manylinux2014_x86_64`), so pip installs a real wheel with no
   compiler and no `pg_config` involved, on 3.11 or 3.14 alike. Never
   pin this back down to `2.9.9` — that version predates Python 3.14
   support entirely, wheel or no wheel.

If you actually need a specific Python version and `runtime.txt` isn't
being honored, set it explicitly instead via the **"Advanced settings"**
dialog when you deploy (or redeploy) the app — per Streamlit's docs,
[Python version can only be set at deploy time and can't be changed
afterward](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python);
to change it on an already-deployed app you must delete it and
redeploy with the desired version selected.

## 1b. Enabling PostgreSQL/PostGIS locally (optional)

The Postgres driver (`psycopg2-binary`) is already in the base
`requirements.txt`. The one remaining optional extra is `geoalchemy2`,
needed only for PostGIS `Geometry` columns (`USE_POSTGIS=true`):

```bash
pip install -r requirements.txt -r requirements-postgres.txt
```

Then set `USE_POSTGIS=true` and point `DATABASE_URL` at your Postgres
instance in `.env`.

## 2. Full stack with PostGIS (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

This starts three containers:

- `kwid-app` — the Streamlit dashboard (port 8501, proxied via nginx on 80)
- `kwid-db` — PostgreSQL 16 + PostGIS 3.4
- `kwid-nginx` — reverse proxy with WebSocket support (required for Streamlit's live channel)

`docker-compose.yml` sets `USE_POSTGIS=true` and points `DATABASE_URL`
at the `kwid-db` service automatically.

Initialize/seed the database inside the running container:

```bash
docker compose exec kwid-app python -m database.initialize
```

## 3. Enabling live external data sources

Edit `.env` and set the relevant credentials:

```
WRA_API=...
WASREB_API=...
NASA_API=...        # NASA POWER is keyless; leave blank
COPERNICUS_API_KEY=...

# CHIRPS is sourced from Google Earth Engine, not a plain REST key —
# see the dedicated setup below.
```

No code changes are required — `api/base.py`'s `safe_fetch()` will use
the live endpoint whenever it succeeds, and only fall back to synthetic
data on failure. See `docs/API_GUIDE.md`.

### CHIRPS / Google Earth Engine setup

CHIRPS rainfall (`api/chirps.py`) queries Google Earth Engine directly
instead of a REST wrapper. Steps:

1. Enable the Earth Engine API on a Google Cloud project and, for
   server/Docker/CI use, create a service account with the
   **Earth Engine Resource Viewer** role and download its JSON key.
2. `pip install earthengine-api` (already in `requirements.txt`).
3. Set in `.env`:
   ```
   GEE_SERVICE_ACCOUNT_EMAIL=my-sa@my-project.iam.gserviceaccount.com
   GEE_SERVICE_ACCOUNT_KEY_FILE=/secure/path/to/key.json
   GEE_PROJECT_ID=my-gcp-project
   ```
   For local/interactive use instead, run `earthengine authenticate`
   once and just set `GEE_PROJECT_ID`.
4. Leave all three blank to keep using the synthetic fallback rainfall
   data with no errors.

## 4. Using official county boundaries

Replace the bundled simplified GeoJSON with the real Kenya county
shapefile (e.g. from IEBC or KNBS) at:

```
data/counties/kenya_counties.shp   (+ .shx, .dbf, .prj siblings)
```

`gis/county_loader.py` automatically prefers the shapefile over the
bundled GeoJSON when present.

## 5. Optional: build the Svelte header

```bash
cd frontend
npm install
npm run build
```

`components/header.py` auto-detects `frontend/dist/index.html` and
embeds it; the app runs fine without this step.

## 6. Running tests

```bash
pip install pytest
pytest -q
```

## 7. Retraining ML models

```bash
python -m ml.train
```
