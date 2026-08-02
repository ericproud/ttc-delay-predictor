import pandas as pd
from openmeteo_requests import Client

TORONTO_LAT = 43.6532
TORONTO_LON = -79.3832
DEFAULT_TIMEZONE = "America/Toronto"

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARIABLES = ["temperature_2m", "precipitation", "wind_speed_10m", "snow_depth"]

METERS_TO_MM = 1000


def get_hourly_weather_range(
    client: Client,
    url: str,
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
    tz: str,
) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": HOURLY_VARIABLES,
        "timezone": tz,
    }
    response = client.weather_api(url, params=params)[0]
    hourly = response.Hourly()

    time_range = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(tz),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert(tz),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    )

    return pd.DataFrame(
        {
            "datetime": time_range,
            "temp_c": hourly.Variables(0).ValuesAsNumpy(),
            "precipitation_mm": hourly.Variables(1).ValuesAsNumpy(),
            "wind_speed_kmh": hourly.Variables(2).ValuesAsNumpy(),
            "snow_depth_mm": hourly.Variables(3).ValuesAsNumpy() * METERS_TO_MM,
        }
    )
