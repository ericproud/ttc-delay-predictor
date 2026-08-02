from datetime import date, time

import requests
import streamlit as st

st.set_page_config(page_title="TTC Delay Predictor", page_icon="🚇")
st.title("TTC Subway Delay Predictor")
st.caption(
    "Predicts incident duration using the trained CatBoost model, "
    "with live forecast weather auto-fetched by the API."
)

api_base_url = st.sidebar.text_input("API base URL", value="http://localhost:5000")


@st.cache_data(ttl=3600)
def fetch_categories(base_url: str) -> dict:
    response = requests.get(f"{base_url}/services/categories", timeout=10)
    response.raise_for_status()
    return response.json()


try:
    categories = fetch_categories(api_base_url)
except requests.exceptions.RequestException:
    st.error(f"Couldn't reach the API at {api_base_url} -- is it running?")
    st.stop()

code_descriptions = {c["code"]: c["description"] for c in categories["codes"]}
code_options = [c["code"] for c in categories["codes"]]


def format_code(code: str) -> str:
    return f"{code} — {code_descriptions[code]}" if code_descriptions.get(code) else code


station_options_by_line = categories["stations_by_line"]

# Outside the form: selecting a line must rerun the script immediately so the
# station dropdown below can be filtered to that line's stations. Widgets
# inside st.form() only take effect on submit, which would be too late here.
line = st.selectbox("Line", options=categories["lines"])

with st.form("predict_form"):
    station = st.selectbox("Station", options=station_options_by_line.get(line, []))
    bound = st.selectbox("Bound", options=categories["bounds"])
    code = st.selectbox("Incident code", options=code_options, format_func=format_code)
    incident_date = st.date_input("Date", value=date.today())
    incident_time = st.time_input("Time", value=time(8, 0))
    submitted = st.form_submit_button("Predict delay")

if submitted:
    # The API only takes a whole hour (0-23) -- round the picked time to the
    # nearest one rather than truncating, so 8:47 becomes 9, not 8.
    rounded_hour = incident_time.hour + (1 if incident_time.minute >= 30 else 0)
    rounded_hour %= 24
    st.caption(
        f"Using hour {rounded_hour:02d}:00 for the prediction (rounded from {incident_time.strftime('%H:%M')})."
    )

    payload = {
        "line": line,
        "station": station,
        "bound": bound,
        "code": code,
        "date": incident_date.isoformat(),
        "hour": rounded_hour,
    }

    try:
        response = requests.post(f"{api_base_url}/services/predict", json=payload, timeout=15)
    except requests.exceptions.ConnectionError:
        st.error(f"Couldn't reach the API at {api_base_url} -- is it running?")
    else:
        if response.status_code == 200:
            result = response.json()
            st.metric("Predicted delay", f"{result['prediction']:.1f} min")
            if result["confidence"] == "Confident":
                st.success("Confidence: Confident")
            else:
                st.warning(
                    "Confidence: Not Confident -- predictions above 15 minutes "
                    "are less reliable (see the model's known tail-underprediction issue)."
                )
        else:
            body = response.json()
            if body.get("errors"):
                # Validation errors -- one or more, each tied to a field.
                for err in body["errors"]:
                    st.error(f"{err['field']}: {err['message']}")
            else:
                message = (
                    body.get("error", {}).get("message") or body.get("detail") or response.text
                )
                st.error(f"{response.status_code}: {message}")
