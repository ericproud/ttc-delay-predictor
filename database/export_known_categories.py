import json
from pathlib import Path

from database.queries import get_code_descriptions, get_known_categories
from database.ttc_delays.config import LINE_STATIONS

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "services" / "known_categories.json"


def export_known_categories() -> None:
    categories = get_known_categories()
    known_stations = categories["stations"]

    snapshot = {
        "lines": sorted(categories["lines"]),
        "stations": sorted(known_stations),
        "bounds": sorted(categories["bounds"]),
        "codes": sorted(categories["codes"]),
        "stations_by_line": {
            line: sorted(stations & known_stations) for line, stations in LINE_STATIONS.items()
        },
        "code_descriptions": get_code_descriptions(),
    }

    OUTPUT_PATH.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote known-categories snapshot to {OUTPUT_PATH}")


if __name__ == "__main__":
    export_known_categories()
