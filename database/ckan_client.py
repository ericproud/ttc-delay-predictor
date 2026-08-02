import io
from collections.abc import Callable
from typing import Any

import pandas as pd
import requests

from database.config import CKAN_PACKAGE_URL, DATASET_ID


def get_ckan_resources() -> list[dict[str, Any]]:
    print("Querying CKAN API for TTC subway delay dataset resources...\n")

    res = requests.get(CKAN_PACKAGE_URL, params={"id": DATASET_ID})
    res.raise_for_status()

    return res.json()["result"]["resources"]


def download_resource(resource: dict[str, Any]) -> pd.DataFrame:
    print(f"Downloading {resource['name']}...\n")

    response = requests.get(resource["url"])
    response.raise_for_status()
    stream = io.BytesIO(response.content)

    if resource["url"].endswith(".xlsx"):
        sheets = pd.read_excel(stream, sheet_name=None)
        return pd.concat(sheets.values(), ignore_index=True)
    return pd.read_csv(stream)


def build_dataframe(
    get_dataset_resources: Callable[[], list[dict[str, Any]]],
    clean_df: Callable[[pd.DataFrame], pd.DataFrame],
) -> pd.DataFrame:
    cleaned_dfs = [clean_df(download_resource(resource)) for resource in get_dataset_resources()]
    return pd.concat(cleaned_dfs, ignore_index=True)
