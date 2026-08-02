import pandas as pd

from database.db import get_connection
from database.delay_codes.get_df import get_delay_code_metadata_df
from database.toronto_weather.get_df import get_toronto_weather_df
from database.ttc_delays.get_df import get_ttc_delays_df


def populate_db() -> None:
    ttc_delays_df = get_ttc_delays_df()
    delay_code_metadata_df = get_delay_code_metadata_df()
    toronto_weather_df = get_toronto_weather_df()

    insert_df_into_db(ttc_delays_df, "delays")
    insert_df_into_db(delay_code_metadata_df, "delay_code_metadata")
    insert_df_into_db(toronto_weather_df, "toronto_weather")


def insert_df_into_db(df: pd.DataFrame, table_name: str) -> None:
    print(f"Refreshing {table_name}...\n")

    columns_str = ", ".join(df.columns)
    rows = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in df.itertuples(index=False, name=None)
    ]

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY")
                with cur.copy(f"COPY {table_name} ({columns_str}) FROM STDIN") as copy:
                    for row in rows:
                        copy.write_row(row)
            conn.commit()
            print(f"{table_name} refreshed with {len(rows)} rows!\n")
    except Exception as e:
        print(f"Failed to refresh {table_name}: {e}\n")


if __name__ == "__main__":
    populate_db()
