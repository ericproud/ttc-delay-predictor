from typing import Any

import joblib
import pandas as pd
from catboost import CatBoostRegressor

from model.config import FEATURE_COLUMNS, MODEL_PATH
from model.features import prepare_incident_features
from model.utils import convert_prediction_to_float, transform_log_to_minutes
from services.schemas import PredictionResponse

model: CatBoostRegressor | None = None


def load_model() -> CatBoostRegressor:
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model


def build_feature_row(
    validated_fields: dict[str, Any], weather_fields: dict[str, Any]
) -> pd.DataFrame:
    all_fields = {**validated_fields, **weather_fields}
    df = pd.DataFrame([all_fields])
    return prepare_incident_features(df)[FEATURE_COLUMNS]


def predict_delay_duration(
    validated_fields: dict[str, Any], weather_fields: dict[str, Any]
) -> PredictionResponse:
    model = load_model()
    df = build_feature_row(validated_fields, weather_fields)

    prediction_log = model.predict(df)
    prediction_minutes = transform_log_to_minutes(prediction_log)
    prediction_float = convert_prediction_to_float(prediction_minutes)

    return PredictionResponse(
        prediction=prediction_float,
        confidence="Confident" if prediction_float < 15 else "Not Confident",
    )
