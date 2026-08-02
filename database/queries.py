from typing import Any

import pandas as pd

from database.db import get_connection


def get_all_delays() -> pd.DataFrame:
    query = """
        SELECT * FROM v_delays_expanded
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_delays_by_range(start_date: str, end_date: str) -> pd.DataFrame:
    query = """
        SELECT * FROM v_delays_expanded
        WHERE date >= %s AND date <= %s
        ORDER BY date DESC, time DESC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[start_date, end_date])


def get_station_delay_summary() -> pd.DataFrame:
    query = """
        SELECT
            station,
            line,
            COUNT(*) AS total_incidents,
            SUM(min_delay) AS total_delay_minutes,
            AVG(min_delay)::NUMERIC(10,2) AS avg_delay_minutes
        FROM delays
        GROUP BY station, line
        ORDER BY total_delay_minutes DESC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_top_delay_reasons(num_reasons: int) -> pd.DataFrame:
    query = """
        SELECT
            code,
            description,
            COUNT(*) AS total_incidents,
            SUM(min_delay) AS total_delay_minutes,
            AVG(min_delay)::NUMERIC(10,2) AS avg_delay_minutes
        FROM v_delays_expanded
        GROUP BY code, description
        ORDER BY total_incidents DESC
        LIMIT %s;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[num_reasons])


def get_delays_by_hour() -> pd.DataFrame:
    query = """
        SELECT
            EXTRACT(HOUR FROM time) AS hour_of_day,
            COUNT(*) AS total_incidents,
            SUM(min_delay) AS total_delay_minutes,
            AVG(min_delay)::NUMERIC(10,2) AS avg_delay_minutes
        FROM delays
        GROUP BY hour_of_day
        ORDER BY hour_of_day ASC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_delay_codes() -> pd.DataFrame:
    query = """
    SELECT * FROM delay_code_metadata
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def get_delays_with_weather(
    start_date: str | None = None, end_date: str | None = None
) -> pd.DataFrame:
    query = """
        SELECT * FROM v_delays_with_weather
        WHERE (%(start_date)s IS NULL OR date >= %(start_date)s)
          AND (%(end_date)s IS NULL OR date <= %(end_date)s)
        ORDER BY date DESC, time DESC;
    """
    params: dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def get_known_categories() -> dict[str, set[str]]:
    query = """
    SELECT
        array_agg(DISTINCT line) FILTER (WHERE line IS NOT NULL) AS lines,
        array_agg(DISTINCT station) FILTER (WHERE station IS NOT NULL) AS stations,
        array_agg(DISTINCT bound) FILTER (WHERE bound IS NOT NULL) AS bounds,
        array_agg(DISTINCT code) FILTER (WHERE code IS NOT NULL) AS codes
    FROM v_delays_with_weather
    WHERE min_delay > 0 AND line IS NOT NULL AND station IS NOT NULL;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        row = cur.fetchone()
        assert row is not None  # a bare aggregate query always returns exactly one row
        lines, stations, bounds, codes = row

    return {
        "lines": {v.upper() for v in (lines or [])},
        "stations": {v.upper() for v in (stations or [])},
        "bounds": {v.upper() for v in (bounds or [])},
        "codes": {v.upper() for v in (codes or [])},
    }


def get_code_descriptions() -> dict[str, str]:
    query = """
    SELECT DISTINCT code, description
    FROM v_delays_with_weather
    WHERE min_delay > 0 AND line IS NOT NULL AND station IS NOT NULL
          AND code IS NOT NULL AND description IS NOT NULL
    ORDER BY code;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return {code.upper(): description for code, description in rows}


def get_raw_incident_level_data() -> pd.DataFrame:
    query = """
    SELECT
        date,
        EXTRACT(HOUR FROM time)::int AS hour,
        line,
        station,
        bound,
        code,
        description,
        min_delay,
        COALESCE(temp_c, 0.0) AS temp_c,
        COALESCE(precipitation_mm, 0.0) AS precipitation_mm,
        COALESCE(snow_depth_mm, 0.0) AS snow_depth_mm,
        COALESCE(wind_speed_kmh, 0.0) AS wind_speed_kmh
    FROM
        v_delays_with_weather
    WHERE
        min_delay > 0
        AND line IS NOT NULL
        AND station IS NOT NULL
    ORDER BY
        date ASC,
        time ASC;
    """
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)
