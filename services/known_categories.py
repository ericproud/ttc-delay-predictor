import json
from pathlib import Path

# Bundled snapshot of valid lines/stations/bounds/codes + descriptions, so the
# API/Streamlit app run with no database configured. Regenerate it after
# retraining on new data with `python -m database.export_known_categories`
# (requires SUPABASE_DB_URI).
_SNAPSHOT_PATH = Path(__file__).resolve().parent / "known_categories.json"
_snapshot = json.loads(_SNAPSHOT_PATH.read_text(encoding="utf-8"))

KNOWN_LINES = set(_snapshot["lines"])
KNOWN_STATIONS = set(_snapshot["stations"])
KNOWN_BOUNDS = set(_snapshot["bounds"])
KNOWN_CODES = set(_snapshot["codes"])
STATIONS_BY_LINE = _snapshot["stations_by_line"]
CODE_DESCRIPTIONS = _snapshot["code_descriptions"]
