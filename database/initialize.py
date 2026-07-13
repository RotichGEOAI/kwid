"""
database/initialize.py
Creates all tables and seeds the database from the bundled synthetic
Kenya county dataset (data/counties/kenya_counties.csv) if it's empty.
Run standalone with:  python -m database.initialize
"""
import csv
import random

from config import Config
from core.logging_config import get_logger
from database.connection import engine, get_session
from database.models import Base, County, Borehole, WaterStatistic

logger = get_logger(__name__)


def create_all_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created (or already existed).")


def seed_from_csv(csv_path=None):
    csv_path = csv_path or Config.COUNTY_CSV
    if not csv_path.exists():
        logger.warning("Seed CSV not found at %s — skipping seed.", csv_path)
        return

    with get_session() as db:
        if db.query(County).count() > 0:
            logger.info("Counties table already populated — skipping seed.")
            return

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            rng = random.Random(7)
            for row in reader:
                county = County(
                    name=row["county"],
                    lat=float(row["lat"]),
                    lon=float(row["lon"]),
                    population=int(float(row["population"])),
                    area_km2=float(row["area_km2"]),
                )
                db.add(county)
                db.flush()  # get county.id

                stat = WaterStatistic(
                    county_id=county.id,
                    borehole_density_per_km2=float(row["borehole_density_per_km2"]),
                    distance_to_water_km=float(row["distance_to_water_km"]),
                    rainfall_mm_annual=float(row["rainfall_mm_annual"]),
                    water_scarcity_index=float(row["water_scarcity_index"]),
                    water_quality_risk_index=float(row["water_quality_risk_index"]),
                    groundwater_recharge_mm=float(row["groundwater_recharge_mm"]),
                    rainwater_harvesting_suitability=float(row["rainwater_harvesting_suitability"]),
                    improved_water_access_pct=float(row["improved_water_access_pct"]),
                )
                db.add(stat)

                n_boreholes = int(row["boreholes"])
                for _ in range(min(n_boreholes, 25)):  # cap per-county rows for demo speed
                    db.add(Borehole(
                        county_id=county.id,
                        lat=county.lat + rng.uniform(-0.12, 0.12),
                        lon=county.lon + rng.uniform(-0.12, 0.12),
                        depth_m=round(rng.uniform(20, 220), 1),
                        yield_m3_per_hr=round(rng.uniform(0.5, 15), 2),
                        status=rng.choices(
                            ["active", "dry", "abandoned"], weights=[0.78, 0.14, 0.08]
                        )[0],
                        drilled_year=rng.randint(1985, 2025),
                        source="WRA (synthetic seed)",
                    ))

        logger.info("Seeded %d counties from %s", db.query(County).count(), csv_path)


def initialize():
    create_all_tables()
    seed_from_csv()


if __name__ == "__main__":
    initialize()
    print("Database initialized.")
