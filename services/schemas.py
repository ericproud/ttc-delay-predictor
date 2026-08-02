from datetime import date as date_type
from datetime import timedelta
from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator

from database.ttc_delays.config import LINE_STATIONS
from services.config import MAX_FORECAST_DAYS
from services.known_categories import KNOWN_BOUNDS, KNOWN_CODES, KNOWN_LINES, KNOWN_STATIONS

KNOWN_VALUES = {
    "line": KNOWN_LINES,
    "station": KNOWN_STATIONS,
    "bound": KNOWN_BOUNDS,
    "code": KNOWN_CODES,
}


class PredictionRequest(BaseModel):
    line: str
    station: str
    bound: str
    code: str
    date: date_type
    hour: int = Field(ge=0, le=23)

    @field_validator("line", "station", "bound", "code")
    @classmethod
    def normalize_and_check_known(cls, value: str, info: ValidationInfo) -> str:
        assert info.field_name is not None  # always set for a field_validator
        normalized = str(value).strip().upper()
        if normalized not in KNOWN_VALUES[info.field_name]:
            raise ValueError(f"unrecognized value: {value!r}")
        return normalized

    @field_validator("date")
    @classmethod
    def check_forecast_window(cls, value: date_type) -> date_type:
        today = date_type.today()
        if not (today <= value <= today + timedelta(days=MAX_FORECAST_DAYS)):
            raise ValueError(
                f"must be within the next {MAX_FORECAST_DAYS} days "
                f"(forecast weather isn't available beyond that)"
            )
        return value

    @model_validator(mode="after")
    def check_station_on_line(self) -> "PredictionRequest":
        if self.station not in LINE_STATIONS.get(self.line, set()):
            raise ValueError(f"{self.station!r} is not on {self.line!r}")
        return self


class PredictionResponse(BaseModel):
    prediction: float
    confidence: Literal["Confident", "Not Confident"]
