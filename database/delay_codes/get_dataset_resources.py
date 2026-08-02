from typing import Any

from database.ckan_client import get_ckan_resources

from .config import DATASET_NAME


def get_delay_code_metadata_dataset_resources() -> list[dict[str, Any]]:
    resources = [r for r in get_ckan_resources() if DATASET_NAME in r.get("name", "")]

    print("Delay code metadata resources retrieved!\n")
    return resources
