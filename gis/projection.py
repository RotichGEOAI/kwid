"""
gis/projection.py
Coordinate reference system helpers. Kenya's official metric CRS for
area/distance-accurate analysis is Arc 1960 / UTM Zone 37S (EPSG:21037).
"""
from core.constants import WGS84_EPSG, KENYA_ARC1960_UTM_EPSG


def to_metric(gdf):
    """Reproject a WGS84 GeoDataFrame to Kenya's metric CRS for area/distance ops."""
    return gdf.to_crs(epsg=KENYA_ARC1960_UTM_EPSG)


def to_geographic(gdf):
    """Reproject back to WGS84 (lat/lon) for web mapping (Plotly/Leaflet/Mapbox)."""
    return gdf.to_crs(epsg=WGS84_EPSG)
