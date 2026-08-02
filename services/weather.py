from datetime import date as date_type

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from services.config import (
    WEATHER_CACHE_DIR,
    WEATHER_CACHE_EXPIRE_SECONDS,
    WEATHER_CACHE_PATH,
    WEATHER_REQUEST_BACKOFF_FACTOR,
    WEATHER_REQUEST_RETRIES,
)
from weather_client import (
    DEFAULT_TIMEZONE,
    FORECAST_URL,
    TORONTO_LAT,
    TORONTO_LON,
    get_hourly_weather_range,
)

WEATHER_CACHE_DIR.mkdir(exist_ok=True)
cache_session = requests_cache.CachedSession(
    WEATHER_CACHE_PATH, expire_after=WEATHER_CACHE_EXPIRE_SECONDS
)
retry_session = retry(
    cache_session, retries=WEATHER_REQUEST_RETRIES, backoff_factor=WEATHER_REQUEST_BACKOFF_FACTOR
)
openmeteo = openmeteo_requests.Client(session=retry_session)


def get_hourly_weather(
    date: date_type | str,
    hour: int,
    lat: float = TORONTO_LAT,
    lon: float = TORONTO_LON,
    tz: str = DEFAULT_TIMEZONE,
) -> dict[str, float]:
    target_datetime = (pd.to_datetime(date) + pd.to_timedelta(hour, unit="h")).tz_localize(tz)
    date_str = target_datetime.strftime("%Y-%m-%d")

    df = get_hourly_weather_range(openmeteo, FORECAST_URL, lat, lon, date_str, date_str, tz)

    target_hour = target_datetime.floor("h")
    idx = (df["datetime"] - target_hour).abs().idxmin()

    return {
        "temp_c": float(df["temp_c"].loc[idx]),
        "snow_depth_mm": float(df["snow_depth_mm"].loc[idx]),
        "wind_speed_kmh": float(df["wind_speed_kmh"].loc[idx]),
        "precipitation_mm": float(df["precipitation_mm"].loc[idx]),
    }
