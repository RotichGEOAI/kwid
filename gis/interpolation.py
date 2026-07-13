"""
gis/interpolation.py
IDW (Inverse Distance Weighting) and Kriging surface interpolation,
used for the water-scarcity and distance-to-water continuous surfaces.
Kriging uses pykrige when available; otherwise transparently falls
back to IDW so the app has no hard dependency on a compiled Fortran
extension (pykrige) being installable in every environment.
"""
import numpy as np

from core.logging_config import get_logger

logger = get_logger(__name__)

try:
    from pykrige.ok import OrdinaryKriging
    _HAS_PYKRIGE = True
except ImportError:  # pragma: no cover
    _HAS_PYKRIGE = False


def idw(lats, lons, values, grid_lats, grid_lons, power=2, epsilon=1e-6):
    lats, lons, values = map(lambda a: np.asarray(a, dtype=float), (lats, lons, values))
    glat, glon = np.meshgrid(grid_lats, grid_lons, indexing="ij")
    out = np.zeros(glat.shape)

    for i in range(glat.shape[0]):
        for j in range(glat.shape[1]):
            d = np.sqrt((lats - glat[i, j]) ** 2 + (lons - glon[i, j]) ** 2) + epsilon
            w = 1.0 / d ** power
            out[i, j] = np.sum(w * values) / np.sum(w)
    return out


def kriging(lats, lons, values, grid_lats, grid_lons):
    """
    Ordinary Kriging surface. Falls back to IDW if pykrige isn't
    installed in the current environment.
    """
    if not _HAS_PYKRIGE:
        logger.info("pykrige not installed — falling back to IDW for kriging() call.")
        return idw(lats, lons, values, grid_lats, grid_lons)

    ok = OrdinaryKriging(
        np.asarray(lons, dtype=float), np.asarray(lats, dtype=float), np.asarray(values, dtype=float),
        variogram_model="spherical", verbose=False, enable_plotting=False,
    )
    z, _ss = ok.execute("grid", grid_lons, grid_lats)
    return np.asarray(z)
