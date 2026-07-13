"""
gis/validation.py
Basic geometry QA used before any spatial analysis runs, so a single
malformed polygon (self-intersection, null geometry) doesn't silently
corrupt density/interpolation outputs.
"""
from core.logging_config import get_logger

logger = get_logger(__name__)


def validate(gdf) -> bool:
    if gdf.empty:
        logger.error("GeoDataFrame is empty.")
        return False
    if gdf.geometry.isna().any():
        logger.error("GeoDataFrame contains null geometries.")
        return False
    invalid = ~gdf.is_valid
    if invalid.any():
        logger.warning("%d invalid geometries found — attempting buffer(0) fix.", invalid.sum())
        gdf.loc[invalid, gdf.geometry.name] = gdf.loc[invalid, gdf.geometry.name].buffer(0)
    return bool(gdf.is_valid.all())
