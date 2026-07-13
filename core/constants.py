"""
core/constants.py
Central location for static, non-secret constants used across KWID.
Keeping these in one module avoids "magic numbers/strings" scattered
through the codebase and makes the wireframe panel titles, thresholds
and color scales auditable in one place.
"""

APP_NAME = "Kenya Water Intelligence Dashboard"
APP_SHORT = "KWID"
AUTHOR = "Rotich"
AUTHOR_TITLE = "GIS & GEOAI Analyst"

# CRS
WGS84_EPSG = 4326
KENYA_ARC1960_UTM_EPSG = 21037  # Arc 1960 / UTM zone 37S — metric CRS for Kenya

# Panel titles - mirror the original infographic wireframe 1:1
PANEL_TITLES = {
    "heatmap": "Borehole Density Heat Map",
    "scarcity": "Water Scarcity",
    "distance": "Distance to Water",
    "county_table": "County Statistics",
    "water_quality": "Water Quality Risks",
    "risks": "Risk Flags",
    "rainwater": "Rainwater Harvesting Suitability",
    "recommendations": "Recommendations",
}

# Risk / scarcity thresholds (0-1 normalized indices)
SCARCITY_THRESHOLDS = {"low": 0.33, "moderate": 0.66, "high": 1.01}
RISK_THRESHOLDS = {"low": 0.33, "moderate": 0.66, "high": 1.01}

COLOR_SCALE_DENSITY = "YlGnBu"
COLOR_SCALE_SCARCITY = "OrRd"
COLOR_SCALE_RISK = "Reds"
COLOR_SCALE_SUITABILITY = "Greens"

DEFAULT_MAP_CENTER = {"lat": 0.0236, "lon": 37.9062}  # Kenya centroid
DEFAULT_MAP_ZOOM = 5.4

KENYA_COUNTY_COUNT = 47

CACHE_TTL_SECONDS = 3600  # default cache lifetime for external API calls
