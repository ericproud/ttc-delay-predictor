import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def transform_target_to_log(y_minutes: np.ndarray) -> np.ndarray:
    return np.log1p(y_minutes)


def transform_log_to_minutes(preds_log: np.ndarray) -> np.ndarray:
    preds_minutes = np.expm1(preds_log)
    return np.clip(preds_minutes, a_min=0, a_max=None)


def convert_prediction_to_float(prediction: np.ndarray) -> float:
    return float(prediction[0])


def evaluate_model(y_true: pd.Series, y_pred: np.ndarray, max_delay: int = 60) -> dict[str, float]:
    mask = y_true <= max_delay
    y_t, y_p = y_true[mask], y_pred[mask]

    return {
        "MAE": mean_absolute_error(y_t, y_p),
        "RMSE": np.sqrt(mean_squared_error(y_t, y_p)),
        "R2": r2_score(y_t, y_p),
    }
