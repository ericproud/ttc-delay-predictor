from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "catboost_incident_regressor.joblib"

TARGET_COLUMN = "min_delay"
TRAIN_END_DATE = "2023-12-31"

CATEGORICAL_FEATURES = [
    "line",
    "station",
    "bound",
    "code",
    "day_of_week",
    "line_code",
    "station_code",
]

NUMERIC_FEATURES = [
    "hour_sin",
    "hour_cos",
    "is_peak_hour",
    "temp_c",
    "precipitation_mm",
    "snow_depth_mm",
    "wind_speed_kmh",
]

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES

CATBOOST_PARAMS = {
    "iterations": 1000,
    "learning_rate": 0.03,
    "depth": 5,
    "l2_leaf_reg": 10,
    "subsample": 0.8,
    "rsm": 0.7,
    "loss_function": "RMSE",
    "eval_metric": "RMSE",
    "random_seed": 42,
    "verbose": 100,
}
