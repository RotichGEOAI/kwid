"""
gis/kde.py
Kernel Density Estimation for the "Borehole Density Heat Map" panel.
Uses scikit-learn's KernelDensity with a haversine metric so bandwidth
is interpretable in real distance units even though inputs are lat/lon.
"""
import numpy as np
from sklearn.neighbors import KernelDensity


def borehole_kde(lats, lons, bandwidth_km=25, grid_size=60, bbox=None):
    """
    Returns (grid_lats, grid_lons, density) suitable for a Plotly
    Densitymapbox / contour layer.

    bandwidth_km: KDE bandwidth in kilometers (haversine metric expects
                  radians, so we convert bandwidth_km -> radians).
    bbox: (south, west, north, east); defaults to data bounds w/ padding.
    """
    lats = np.asarray(lats, dtype=float)
    lons = np.asarray(lons, dtype=float)
    if len(lats) < 2:
        raise ValueError("Need at least 2 points for KDE.")

    coords_rad = np.radians(np.column_stack([lats, lons]))
    bandwidth_rad = bandwidth_km / 6371.0088  # earth radius km

    kde = KernelDensity(bandwidth=bandwidth_rad, metric="haversine", kernel="gaussian")
    kde.fit(coords_rad)

    if bbox is None:
        pad = 0.5
        south, north = lats.min() - pad, lats.max() + pad
        west, east = lons.min() - pad, lons.max() + pad
    else:
        south, west, north, east = bbox

    grid_lats = np.linspace(south, north, grid_size)
    grid_lons = np.linspace(west, east, grid_size)
    glat, glon = np.meshgrid(grid_lats, grid_lons, indexing="ij")
    grid_rad = np.radians(np.column_stack([glat.ravel(), glon.ravel()]))

    log_density = kde.score_samples(grid_rad)
    density = np.exp(log_density).reshape(glat.shape)
    density = density / density.max()  # normalize 0-1 for consistent color scaling

    return grid_lats, grid_lons, density
