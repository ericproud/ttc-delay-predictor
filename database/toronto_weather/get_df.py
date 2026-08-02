from datetime import datetime

import openmeteo_requests
import pandas as pd

from weather_client import (
    ARCHIVE_URL,
    DEFAULT_TIMEZONE,
    TORONTO_LAT,
    TORONTO_LON,
    get_hourly_weather_range,
)

from .config import START_DAY, START_MONTH, START_YEAR


def get_toronto_weather_df() -> pd.DataFrame:
    start_date = datetime(START_YEAR, START_MONTH, START_DAY).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    print("Fetching historical weather data from 2014 to present...")

    client = openmeteo_requests.Client()
    weather_df = get_hourly_weather_range(
        client, ARCHIVE_URL, TORONTO_LAT, TORONTO_LON, start_date, end_date, DEFAULT_TIMEZONE
    )

    weather_df["temp_c"] = weather_df["temp_c"].ffill().bfill()
    weather_df["wind_speed_kmh"] = weather_df["wind_speed_kmh"].ffill().bfill()
    weather_df["precipitation_mm"] = weather_df["precipitation_mm"].fillna(0.0)
    weather_df["snow_depth_mm"] = weather_df["snow_depth_mm"].fillna(0.0)

    weather_df["date"] = weather_df["datetime"].dt.strftime("%Y-%m-%d")
    weather_df["hour"] = weather_df["datetime"].dt.hour
    weather_df = weather_df.drop(columns=["datetime"])

    return weather_df.drop_duplicates(subset=["date", "hour"]).reset_index(drop=True)
