"""
database/models.py
SQLAlchemy ORM models. Uses GeoAlchemy2 geometry columns when running
against PostGIS (Config.USE_POSTGIS=True); otherwise plain lat/lon
float columns are used so the schema also works unmodified on SQLite
for local development and demos.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from config import Config

Base = declarative_base()

if Config.USE_POSTGIS:
    try:
        from geoalchemy2 import Geometry
    except ImportError as exc:
        raise ImportError(
            "USE_POSTGIS=true but geoalchemy2 is not installed. Install the "
            "optional Postgres extras with:\n"
            "    pip install -r requirements.txt -r requirements-postgres.txt"
        ) from exc


class County(Base):
    __tablename__ = "counties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    population = Column(Integer)
    area_km2 = Column(Float)

    if Config.USE_POSTGIS:
        geom = Column(Geometry("POLYGON", srid=4326))

    boreholes = relationship("Borehole", back_populates="county")
    water_stats = relationship("WaterStatistic", back_populates="county")

    def __repr__(self):
        return f"<County {self.name}>"


class Borehole(Base):
    __tablename__ = "boreholes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    depth_m = Column(Float)
    yield_m3_per_hr = Column(Float)
    status = Column(String(30), default="active")  # active|dry|abandoned
    drilled_year = Column(Integer)
    source = Column(String(50), default="WRA")

    county = relationship("County", back_populates="boreholes")


class WaterStatistic(Base):
    """One row per county capturing the metrics the wireframe visualizes."""

    __tablename__ = "water_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    county_id = Column(Integer, ForeignKey("counties.id"), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    borehole_density_per_km2 = Column(Float)
    distance_to_water_km = Column(Float)
    rainfall_mm_annual = Column(Float)
    water_scarcity_index = Column(Float)          # 0 (abundant) - 1 (severe)
    water_quality_risk_index = Column(Float)       # 0 (safe) - 1 (high risk)
    groundwater_recharge_mm = Column(Float)
    rainwater_harvesting_suitability = Column(Float)  # 0-1
    improved_water_access_pct = Column(Float)

    county = relationship("County", back_populates="water_stats")


class APIFetchLog(Base):
    """Audit trail of external API calls (Module 3 connectors)."""

    __tablename__ = "api_fetch_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(40), nullable=False)   # WRA, NASA_POWER, CHIRPS, ...
    endpoint = Column(String(255))
    status = Column(String(20))                    # success|fallback|error
    fetched_at = Column(DateTime, default=datetime.utcnow)
    detail = Column(String(500))
