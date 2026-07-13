"""
gis/groundwater.py
Simple, transparent groundwater recharge estimator using a water-
balance style approach (recharge coefficient method):

    Recharge = Rainfall_mm * RechargeCoefficient(soil, land cover)

This is intentionally interpretable (vs. a black-box model) for the
"Groundwater Recharge" GIS-engine deliverable; ml/groundwater_prediction.py
provides the companion machine-learning based potential-mapping model.
"""

# Recharge coefficients by simplified soil/land-cover class (fraction of
# rainfall that reaches the water table) — indicative values from
# published Kenyan hydrogeology studies, used as defaults.
RECHARGE_COEFFICIENTS = {
    "sandy": 0.18,
    "loam": 0.10,
    "clay": 0.04,
    "rock_fractured": 0.14,
    "urban": 0.02,
}


def estimate_recharge_mm(rainfall_mm_annual, soil_class="loam", soil_moisture_index=None):
    coeff = RECHARGE_COEFFICIENTS.get(soil_class, 0.08)
    if soil_moisture_index is not None:
        # Wetter antecedent soil moisture modestly increases recharge efficiency
        coeff *= (1 + 0.3 * soil_moisture_index)
    return round(rainfall_mm_annual * coeff, 1)
