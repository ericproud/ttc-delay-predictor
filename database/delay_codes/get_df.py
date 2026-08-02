import pandas as pd

from database.ckan_client import build_dataframe

from .clean_df import clean_ttc_delay_code_metadata_df
from .get_dataset_resources import get_delay_code_metadata_dataset_resources


def get_delay_code_metadata_df() -> pd.DataFrame:
    return build_dataframe(
        get_delay_code_metadata_dataset_resources, clean_ttc_delay_code_metadata_df
    )
