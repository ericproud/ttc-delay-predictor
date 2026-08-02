from flask import Blueprint, current_app, jsonify, request
from flask.typing import ResponseReturnValue
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from services.known_categories import (
    CODE_DESCRIPTIONS,
    KNOWN_BOUNDS,
    KNOWN_CODES,
    KNOWN_LINES,
    KNOWN_STATIONS,
    STATIONS_BY_LINE,
)
from services.predictor import load_model, predict_delay_duration
from services.schemas import PredictionRequest
from services.weather import get_hourly_weather

main = Blueprint("main", __name__)


@main.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError) -> ResponseReturnValue:
    # Pydantic reports every failing field at once, not just the first --
    # surface all of them rather than making the client fix issues one at a
    # time across repeated requests.
    errors = [
        {
            "field": ".".join(str(part) for part in e["loc"]),
            "message": e["msg"].removeprefix("Value error, "),
        }
        for e in error.errors()
    ]
    return jsonify({"errors": errors}), 400


@main.errorhandler(Exception)
def handle_unexpected_error(error: Exception) -> ResponseReturnValue:
    if isinstance(error, HTTPException):
        return error
    current_app.logger.exception("Unhandled error in prediction request")
    return jsonify({"error": {"message": "Something went wrong processing this request."}}), 500


@main.route("/health", methods=["GET"])
def health() -> ResponseReturnValue:
    try:
        load_model()
    except Exception:
        current_app.logger.exception("Health check: model not available")
        return jsonify({"status": "unhealthy", "detail": "model not available"}), 503
    return jsonify({"status": "ok"})


@main.route("/services/categories", methods=["GET"])
def categories() -> ResponseReturnValue:
    return jsonify(
        {
            "lines": sorted(KNOWN_LINES),
            "stations": sorted(KNOWN_STATIONS),
            "stations_by_line": STATIONS_BY_LINE,
            "bounds": sorted(KNOWN_BOUNDS),
            "codes": [
                {"code": code, "description": CODE_DESCRIPTIONS.get(code, "")}
                for code in sorted(KNOWN_CODES)
            ],
        }
    )


@main.route("/services/predict", methods=["POST"])
def predict() -> ResponseReturnValue:
    request_data = request.get_json() or {}

    validated_request = PredictionRequest(**request_data)
    validated_fields = validated_request.model_dump()

    weather_data = get_hourly_weather(validated_fields["date"], validated_fields["hour"])

    prediction = predict_delay_duration(validated_fields, weather_data)

    return jsonify(prediction.model_dump())
