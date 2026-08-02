import pandas as pd


def clean_ttc_delay_code_metadata_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, [2, 3]].dropna(how="all")  # only columns C and D hold code/description
    df.columns = ["code", "description"]

    df["code"] = df["code"].astype(str).str.strip().str.upper()
    df["description"] = df["description"].astype(str).str.strip()

    df = df[df["code"] != "SUB RMENU CODE"]  # header title leftover, not a real code
    return df.dropna()
