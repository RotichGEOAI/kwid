from gis.county_loader import load_counties_dataframe
from ml.groundwater_prediction import predict_groundwater_potential
from ml.demand_forecast import forecast_demand_m3_per_day


def test_groundwater_predictions_have_expected_length():
    df = load_counties_dataframe()
    preds = predict_groundwater_potential(df)
    assert len(preds) == len(df)
    assert (preds > 0).all()


def test_demand_forecast_positive():
    df = load_counties_dataframe()
    preds = forecast_demand_m3_per_day(df)
    assert len(preds) == len(df)
    assert (preds > 0).all()
