"""
ml/train.py
CLI entry point to (re)train both ML models against the current county
dataset and print evaluation metrics. Run with:  python -m ml.train
"""
from gis.county_loader import load_counties_dataframe
from ml import groundwater_prediction, demand_forecast


def main():
    df = load_counties_dataframe()

    _, gw_metrics = groundwater_prediction.train_model(df)
    print("Groundwater potential model (RandomForest):", gw_metrics)

    _, demand_metrics = demand_forecast.train_model(df)
    print("Water demand model (XGBoost):", demand_metrics)


if __name__ == "__main__":
    main()
