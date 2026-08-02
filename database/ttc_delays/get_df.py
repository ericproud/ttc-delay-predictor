import pandas as pd

from database.ckan_client import build_dataframe

from .clean_df import clean_ttc_delays_df
from .get_dataset_resources import get_ttc_delays_dataset_resources


def get_ttc_delays_df() -> pd.DataFrame:
    return build_dataframe(get_ttc_delays_dataset_resources, clean_ttc_delays_df)
