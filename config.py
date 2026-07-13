"""
config.py
Environment-driven configuration. Nothing secret is hard-coded here;
values are read from the process environment / .env file via
python-dotenv. Import `Config` and use its class attributes.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(val, default=False):
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    # --- App identity ---
    APP_NAME = "Kenya Water Intelligence Dashboard"
    APP_SHORT = "KWID"
    AUTHOR = "Rotich"
    AUTHOR_TITLE = "GIS & GEOAI Analyst"
    ENV = os.getenv("ENV", "development")
    DEBUG = _bool(os.getenv("DEBUG"), default=True)

    # --- Security ---
    SECRET_KEY = os.getenv("SECRET_KEY", "change_me_in_production")

    # --- Database ---
    # Defaults to a local SQLite file so the app runs out-of-the-box.
    # Point DATABASE_URL at a PostgreSQL+PostGIS instance in production, e.g.:
    #   postgresql+psycopg2://user:pass@host:5432/kwid
    DATABASE_URL = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'processed' / 'kwid.db'}"
    )
    USE_POSTGIS = _bool(os.getenv("USE_POSTGIS"), default=False)

    # --- Mapping ---
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

    # --- External data source credentials / endpoints ---
    WRA_API = os.getenv("WRA_API", "")
    WRA_API_BASE_URL = os.getenv("WRA_API_BASE_URL", "https://wra.go.ke/api")

    WASREB_API_BASE_URL = os.getenv("WASREB_API_BASE_URL", "https://wasreb.go.ke/api")
    WASREB_API = os.getenv("WASREB_API", "")

    AQUASTAT_BASE_URL = os.getenv(
        "AQUASTAT_BASE_URL", "https://data.apps.fao.org/aquastat/api/v1"
    )

    NASA_API = os.getenv("NASA_API", "")
    NASA_POWER_BASE_URL = os.getenv(
        "NASA_POWER_BASE_URL", "https://power.larc.nasa.gov/api/temporal/daily/point"
    )

    # CHIRPS rainfall is sourced from Google Earth Engine (see api/chirps.py),
    # not a plain REST endpoint. Configure ONE auth path:
    #   1) Service account (servers/CI/Docker):
    #        GEE_SERVICE_ACCOUNT_EMAIL + GEE_SERVICE_ACCOUNT_KEY_FILE + GEE_PROJECT_ID
    #   2) User/local dev (after running `earthengine authenticate` once):
    #        GEE_PROJECT_ID only
    GEE_SERVICE_ACCOUNT_EMAIL = os.getenv("GEE_SERVICE_ACCOUNT_EMAIL", "")
    GEE_SERVICE_ACCOUNT_KEY_FILE = os.getenv("GEE_SERVICE_ACCOUNT_KEY_FILE", "")
    GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "")

    OSM_OVERPASS_URL = os.getenv(
        "OSM_OVERPASS_URL", "https://overpass-api.de/api/interpreter"
    )

    WORLDPOP_BASE_URL = os.getenv("WORLDPOP_BASE_URL", "https://www.worldpop.org/rest/data")

    KENYA_OPEN_DATA_BASE_URL = os.getenv(
        "KENYA_OPEN_DATA_BASE_URL", "https://kenya.opendataforafrica.org/api"
    )

    COPERNICUS_API_KEY = os.getenv("COPERNICUS_API_KEY", "")
    COPERNICUS_BASE_URL = os.getenv(
        "COPERNICUS_BASE_URL", "https://cds.climate.copernicus.eu/api/v2"
    )

    # --- Networking behaviour ---
    HTTP_TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT_SECONDS", "15"))
    HTTP_MAX_RETRIES = int(os.getenv("HTTP_MAX_RETRIES", "3"))
    # When an external API is unreachable/unauthenticated, fall back to the
    # bundled synthetic seed dataset so the dashboard always renders.
    ALLOW_SYNTHETIC_FALLBACK = _bool(os.getenv("ALLOW_SYNTHETIC_FALLBACK"), default=True)

    # --- Paths ---
    DATA_DIR = BASE_DIR / "data"
    COUNTIES_DIR = DATA_DIR / "counties"
    COUNTY_SHAPEFILE = COUNTIES_DIR / "kenya_counties.shp"
    COUNTY_GEOJSON = COUNTIES_DIR / "kenya_counties.geojson"
    COUNTY_CSV = COUNTIES_DIR / "kenya_counties.csv"

    # --- Frontend ---
    # If a compiled Svelte micro-frontend bundle exists, the Streamlit app
    # embeds it via streamlit.components.v1.html; otherwise it degrades
    # gracefully to native Streamlit + Plotly widgets.
    SVELTE_BUILD_DIR = BASE_DIR / "frontend" / "dist"


Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
(Config.DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
