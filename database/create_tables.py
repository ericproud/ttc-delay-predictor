from database.db import get_connection

CREATE_DELAYS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS delays (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    date DATE NOT NULL,
    time TIME NOT NULL,
    day VARCHAR(16) NOT NULL,

    station VARCHAR(64) NOT NULL,
    line VARCHAR(64),
    bound VARCHAR(16),
    vehicle VARCHAR(64),

    code VARCHAR(16) NOT NULL,
    min_delay INT NOT NULL DEFAULT 0,
    min_gap INT NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_delays_line_station ON delays (line, station);
CREATE INDEX IF NOT EXISTS idx_delays_date ON delays (date DESC);
CREATE INDEX IF NOT EXISTS idx_delays_code ON delays (code);
"""

CREATE_DELAY_CODES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS delay_code_metadata (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(16) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

CREATE_WEATHER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS toronto_weather (
    date DATE NOT NULL,
    hour INT NOT NULL,
    temp_c REAL,
    precipitation_mm REAL,
    snow_depth_mm REAL,
    wind_speed_kmh REAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (date, hour)
);
"""

CREATE_V_DELAYS_EXPANDED_TABLE_SQL = """
CREATE OR REPLACE VIEW v_delays_expanded AS
SELECT
    d.id,
    d.date,
    d.time,
    d.day,
    d.station,
    d.line,
    d.bound,
    d.code,
    COALESCE(m.description, 'Unknown Delay Code') AS description,
    d.vehicle,
    d.min_delay,
    d.min_gap
FROM delays d
LEFT JOIN delay_code_metadata m ON d.code = m.code;
"""

CREATE_V_DELAYS_EXPANDED_W_WEATHER_TABLE_SQL = """
CREATE OR REPLACE VIEW v_delays_with_weather AS
SELECT
    d.*,
    COALESCE(m.description, 'Unknown Delay Code') AS description,
    w.temp_c,
    w.precipitation_mm,
    w.snow_depth_mm,
    w.wind_speed_kmh
FROM delays d
LEFT JOIN delay_code_metadata m ON d.code = m.code
LEFT JOIN toronto_weather w
    ON d.date = w.date
   AND EXTRACT(HOUR FROM d.time)::int = w.hour;
"""


def create_tables() -> None:
    print("Connecting to db...")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                print("Creating tables...")
                cur.execute(CREATE_DELAYS_TABLE_SQL)
                cur.execute(CREATE_DELAY_CODES_TABLE_SQL)
                cur.execute(CREATE_WEATHER_TABLE_SQL)
                cur.execute(CREATE_V_DELAYS_EXPANDED_TABLE_SQL)
                cur.execute(CREATE_V_DELAYS_EXPANDED_W_WEATHER_TABLE_SQL)
            conn.commit()
            print("Successfully created tables!")

    except Exception as e:
        print(f"Failed to create tables: {e}")


if __name__ == "__main__":
    create_tables()
