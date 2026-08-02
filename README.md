# TTC Delay Predictor

Predicts how long a TTC subway delay incident will last, in minutes, given the
line, station, direction, delay code, and time — using historical delay
records enriched with weather data. A CatBoost regression model is served
through a small Flask API, with a Streamlit app as a demo front end.

## Quick start (no database needed)

The trained model (`model/artifacts/`) and a snapshot of valid lines,
stations, and delay codes (`services/known_categories.json`) are committed to
the repo, so the API and demo UI run out of the box — no Postgres/Supabase
setup required unless you want to pull fresh data or retrain the model.

```bash
python -m venv .venv
.venv\Scripts\activate                     # Windows (cmd/PowerShell)
source .venv/bin/activate                  # macOS/Linux
pip install -r requirements-services.txt

flask --app app.app run                    # terminal 1
streamlit run streamlit_app.py             # terminal 2
```

## How it fits together

```
Toronto Open Data (CKAN)  ──┐
                             ├──▶  Supabase Postgres  ──▶  model/train.py  ──▶  model artifact (.joblib)
Open-Meteo (historical)  ───┘                                                        │
                                                                                       ▼
Open-Meteo (forecast) ──▶ services/weather.py ──▶ services/predictor.py ──▶ app/ (Flask API) ──▶ streamlit_app.py
```

1. **`database/`** pulls raw delay data from Toronto's CKAN open data portal
   and historical weather from Open-Meteo, cleans it, and loads it into a
   Supabase Postgres database. Only needed to refresh the data or retrain —
   see "Quick start" above if you just want to run the API/demo.
2. **`model/`** trains a CatBoost regressor on that data (`model/train.py`)
   and serializes the result to `model/artifacts/` (committed to the repo).
3. **`services/`** loads the trained model, fetches live forecast weather for
   a requested date/hour, and turns a request into a prediction. Valid
   lines/stations/codes come from the bundled `services/known_categories.json`
   snapshot, not a live database query.
4. **`app/`** exposes that as a small Flask JSON API.
5. **`streamlit_app.py`** is a demo UI that calls the API.
6. **`notebooks/`** holds the exploratory analysis and model
   evaluation used to arrive at the current feature set and model (these do
   query the database directly).

## Project structure

```
app/                   Flask app factory + routes (the prediction API)
database/                 (all of this needs SUPABASE_DB_URI -- not required to just run the API/demo)
  ckan_client.py          Generic CKAN "list resources / download / build a dataframe" helpers
  delay_codes/            Fetch + clean the delay-code-to-description lookup
  ttc_delays/             Fetch + clean the raw delay incident records
  toronto_weather/        Fetch historical hourly weather for Toronto
  create_tables.py        Creates tables + views in Postgres
  populate_db.py          Runs the three pipelines above and loads Postgres
  queries.py              Read-side queries used by training and the snapshot export
  export_known_categories.py  Regenerates services/known_categories.json from the DB
model/
  config.py               Feature list, paths, CatBoost hyperparameters
  features.py             Feature engineering (temporal + interaction features)
  train.py                Trains the model, evaluates it, saves the artifact
  utils.py                Log-target transform + evaluation metrics
  artifacts/               Trained model file (committed)
services/
  predictor.py            Loads the model artifact, runs a prediction
  weather.py               Live forecast weather lookup for a given date/hour
  schemas.py               Pydantic request/response models + validation
  known_categories.py      Valid lines/stations/bounds/codes, loaded from known_categories.json
  known_categories.json   Bundled snapshot (committed) -- see database/export_known_categories.py
notebooks/                Exploratory analysis and model evaluation notebooks (query the DB directly)
streamlit_app.py          Demo UI
weather_client.py         Shared Open-Meteo client (used by both historical and forecast fetches)
lint.py                   One-command lint/format/type-check runner
```

## Full dev setup (data pipeline / retraining)

Everything below this point is only needed if you want to refresh the data,
retrain the model, or run the notebooks — not to run the API/demo (see
"Quick start" above). Requires Python 3.13 and a Postgres database (this
project targets Supabase's Postgres, accessed over its pooler connection
string).

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt
```

`requirements-dev.txt` pulls in `requirements.txt` (full project/training
environment, including `psycopg` for Postgres access) and
`requirements-services.txt` (the minimal set needed to just run the API, no
database driver) transitively — see the comments in those files for details.

Copy `.env.example` to `.env` and fill in your database connection string:

```bash
cp .env.example .env
```

```
SUPABASE_DB_URI=postgresql://user:password@host:5432/postgres
```

## Data pipeline

Create the schema, then populate it from CKAN + Open-Meteo:

```bash
python -m database.create_tables
python -m database.populate_db
```

This creates three tables (`delays`, `delay_code_metadata`, `toronto_weather`)
and two views (`v_delays_expanded`, `v_delays_with_weather` — delays joined
with delay-code descriptions and, in the second view, hourly weather).

## Training the model

```bash
python -m model.train
```

Reads `v_delays_with_weather` via `database/queries.py`, engineers features
(cyclical hour encoding, peak-hour flag, line/station × delay-code
interactions), does a time-based train/test split (train on incidents up to
`TRAIN_END_DATE` in `model/config.py`, test on everything after), and saves
the fitted model to `model/artifacts/`.

The model is trained and evaluated only on delays up to 60 minutes — very
long incidents are rare outliers that would otherwise dominate the loss. In
practice this means predictions above ~15 minutes are less reliable; both the
API response (`confidence`) and the Streamlit UI flag this.

If the underlying data changed (new lines/stations/delay codes), regenerate
the bundled snapshot so the API picks them up without a database at runtime:

```bash
python -m database.export_known_categories
```

## Running the API

```bash
flask --app app.app run
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `200` if the model artifact loads successfully, `503` otherwise |
| `GET` | `/services/categories` | Known lines, stations (overall and per-line via `stations_by_line`), bounds, and delay codes (with descriptions) — used to populate valid request values |
| `POST` | `/services/predict` | Predicts delay duration for a given incident |

`POST /services/predict` request body:

```json
{
  "line": "LINE 1 (YONGE-UNIVERSITY)",
  "station": "BLOOR-YONGE STATION",
  "bound": "N",
  "code": "MUATC",
  "date": "2026-08-10",
  "hour": 8
}
```

`line`, `station`, `bound`, and `code` are validated against the known values
returned by `/services/categories`, and `station` must actually belong to the
given `line` (checked against `LINE_STATIONS` in
`database/ttc_delays/config.py` — the real subway topology, including
interchange stations that legitimately sit on more than one line). `date`
must fall within the next `MAX_FORECAST_DAYS` days (16, in
`services/config.py`) — Open-Meteo doesn't provide forecast weather beyond
that window.

Response:

```json
{
  "prediction": 8.4,
  "confidence": "Confident"
}
```

## Running the demo UI

With the API running (defaults to `http://localhost:5000`):

```bash
streamlit run streamlit_app.py
```

## Development

Formatting, linting, and type-checking are all enforced with Ruff and mypy:

```bash
python lint.py            # auto-fixes formatting/lint issues, then type-checks
python lint.py --check    # CI mode: reports issues without modifying files
```

A pre-commit hook runs the same Ruff checks on every commit — install it once
with `pre-commit install`.

## Tech stack

- **Data / DB** (pipeline + training only): Postgres (Supabase), psycopg, CKAN API, Open-Meteo API
- **Modeling**: pandas, CatBoost, scikit-learn
- **API**: Flask, Pydantic
- **UI**: Streamlit
- **Tooling**: Ruff, mypy, pre-commit
