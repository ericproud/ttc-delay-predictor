import sys
from pathlib import Path

import joblib
import pandas as pd
from catboost import CatBoostRegressor

# Ensure project root is in path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.queries import get_raw_incident_level_data
from model.config import (
    ARTIFACTS_DIR,
    CATBOOST_PARAMS,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    MODEL_PATH,
    TARGET_COLUMN,
    TRAIN_END_DATE,
)
from model.features import prepare_incident_features
from model.utils import (
    evaluate_model,
    transform_log_to_minutes,
    transform_target_to_log,
)


def time_based_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[df["date"] <= TRAIN_END_DATE].copy()
    test = df[df["date"] > TRAIN_END_DATE].copy()
    return train, test


def train_and_evaluate() -> None:
    print("Fetching raw incident data from database...")
    raw_df = get_raw_incident_level_data()
    df = prepare_incident_features(raw_df)

    train_df, test_df = time_based_split(df)

    train_df = train_df[train_df[TARGET_COLUMN] <= 60]

    X_train = train_df[FEATURE_COLUMNS]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    y_train_log = transform_target_to_log(train_df[TARGET_COLUMN].to_numpy())

    print(f"Training on {len(X_train):,} incidents | Testing on {len(X_test):,} incidents\n")

    model = CatBoostRegressor(cat_features=CATEGORICAL_FEATURES, **CATBOOST_PARAMS)
    model.fit(X_train, y_train_log, early_stopping_rounds=100)

    preds_log = model.predict(X_test)
    preds_minutes = transform_log_to_minutes(preds_log)

    metrics = evaluate_model(y_test, preds_minutes, max_delay=60)

    print("\n==========================================")
    print("=== CatBoost Incident Duration Regressor ===")
    print("==========================================")
    print(f"Mean Absolute Error (MAE): {metrics['MAE']:.2f} minutes")
    print(f"Root Mean Squared Error (RMSE): {metrics['RMSE']:.2f} minutes")
    print(f"R^2 Score: {metrics['R2']:.3f}\n")

    # Feature Importance Summary
    importance = pd.Series(model.get_feature_importance(), index=FEATURE_COLUMNS).sort_values(
        ascending=False
    )

    print("Feature Importances:")
    print(importance)

    # 7. Serialize Artifacts
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel artifact successfully saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_and_evaluate()
