# Kenya Water Intelligence Dashboard (KWID) — production image
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# System deps: psycopg2/curl only. geopandas/pyogrio/shapely/pyproj ship
# self-contained manylinux wheels (bundled GEOS/PROJ/GDAL), so no GDAL
# dev headers are required — this was previously a source of slow/
# fragile builds when a wheel wasn't available for the target Python.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-postgres.txt ./
# docker-compose.yml runs this image against PostGIS (USE_POSTGIS=true),
# so install the Postgres extras here too; libpq-dev above covers the
# rare case a wheel isn't available and psycopg2-binary needs to build.
RUN pip install --no-cache-dir -r requirements.txt -r requirements-postgres.txt

COPY . .

RUN mkdir -p logs data/processed data/raw/_api_cache

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
