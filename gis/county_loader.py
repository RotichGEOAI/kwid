"""
gis/county_loader.py
Loads Kenya county geometries. Prefers a real shapefile
(data/counties/kenya_counties.shp) if present — drop IEBC/KNBS
official boundaries there for production use. Falls back to the
bundled simplified GeoJSON (point-buffer polygons around county
centroids) so the app runs without any external shapefile.
"""
import geopandas as gpd
import pandas as pd

from config import Config
from core.logging_config import get_logger

logger = get_logger(__name__)


def load_counties() -> gpd.GeoDataFrame:
    if Config.COUNTY_SHAPEFILE.exists():
        logger.info("Loading official county shapefile from %s", Config.COUNTY_SHAPEFILE)
        gdf = gpd.read_file(Config.COUNTY_SHAPEFILE)
    elif Config.COUNTY_GEOJSON.exists():
        logger.info("Official shapefile not found — using bundled simplified GeoJSON.")
        gdf = gpd.read_file(Config.COUNTY_GEOJSON)
    else:
        raise FileNotFoundError(
            "No county geometry source found. Provide "
            f"{Config.COUNTY_SHAPEFILE} or {Config.COUNTY_GEOJSON}."
        )

    if gdf.crs is None:
        gdf.set_crs(epsg=Config.WGS84_EPSG if hasattr(Config, "WGS84_EPSG") else 4326, inplace=True)

    return gdf


def load_counties_dataframe() -> pd.DataFrame:
    """Flat (non-geometry) view for tabular/chart components."""
    df = pd.read_csv(Config.COUNTY_CSV)
    return df
