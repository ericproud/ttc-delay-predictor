import difflib
import re
from typing import Any

import pandas as pd

from .config import (
    LINE_1_2_4_STATIONS,
    LINE_CODE_MAP,
    STATION_NAME_LINE_IDENTIFIERS,
    STATION_NAME_NOISE_PATTERNS,
    STATION_NAME_SUBSTITUTIONS,
    TARGET_DELAY_COLUMNS,
    VALID_BOUNDS,
)


def clean_ttc_delays_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")

    available_columns = [col for col in TARGET_DELAY_COLUMNS if col in df.columns]
    df = df[available_columns].copy()

    df["station"] = df["station"].apply(normalize_station_name)
    df = drop_unmatched_stations(df)

    df["line"] = df["line"].astype(str).str.strip().str.upper().map(LINE_CODE_MAP)
    df = df.dropna(subset=["line"]).reset_index(drop=True)

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    df["min_delay"] = pd.to_numeric(df["min_delay"], errors="coerce").fillna(0).astype(int)
    df["min_gap"] = pd.to_numeric(df["min_gap"], errors="coerce").fillna(0).astype(int)

    df["bound"] = df["bound"].apply(lambda b: b if b in VALID_BOUNDS else "N/A")

    # fillna() before astype(str): pandas' default "str" dtype keeps missing
    # values as actual missing through astype(str) rather than stringifying
    # them to "nan", so a post-hoc .replace(["nan"], ...) silently misses them.
    df["vehicle"] = df["vehicle"].fillna("N/A").astype(str).replace(["0", "nan"], "N/A")

    # code is NOT NULL in the delays table; a handful of source rows have it
    # blank. "N/A" won't match anything in delay_code_metadata, so it falls
    # back to v_delays_expanded's existing COALESCE(..., 'Unknown Delay Code').
    df["code"] = df["code"].fillna("N/A").astype(str).str.strip().str.upper().replace("", "N/A")

    return df


def drop_unmatched_stations(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["station"].isin(LINE_1_2_4_STATIONS)].reset_index(drop=True)


def normalize_station_name(entry: Any) -> str:
    if pd.isna(entry) or not entry:
        return "N/A"

    text = str(entry).upper().strip()

    for pattern in STATION_NAME_LINE_IDENTIFIERS:
        text = re.sub(pattern, "", text)
    for pattern, replacement in STATION_NAME_SUBSTITUTIONS:
        text = re.sub(pattern, replacement, text)
    for pattern in STATION_NAME_NOISE_PATTERNS:
        text = re.sub(pattern, "", text)

    text = re.sub(r"[^A-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    candidate = f"{text} STATION" if text else "N/A"

    if candidate in LINE_1_2_4_STATIONS:
        return candidate

    matches = difflib.get_close_matches(candidate, LINE_1_2_4_STATIONS, n=1, cutoff=0.6)
    return matches[0] if matches else "N/A"
