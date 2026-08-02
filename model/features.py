import numpy as np
import pandas as pd

from model.config import CATEGORICAL_FEATURES


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df["day_of_week"] = df["date"].dt.day_name()
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    is_weekday = ~df["day_of_week"].isin(["Saturday", "Sunday"])
    is_rush = df["hour"].between(7, 9) | df["hour"].between(16, 18)
    df["is_peak_hour"] = (is_weekday & is_rush).astype(int)
    return df


def add_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    df["line_code"] = df["line"].astype(str) + "_" + df["code"].astype(str)
    df["station_code"] = df["station"].astype(str) + "_" + df["code"].astype(str)
    return df


def prepare_incident_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df["datetime"] = df["date"] + pd.to_timedelta(df["hour"], unit="h")
    df = df.sort_values("datetime").reset_index(drop=True)

    df = add_temporal_features(df)
    df = add_interaction_features(df)

    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].fillna("UNKNOWN").astype(str).str.upper()

    return df
