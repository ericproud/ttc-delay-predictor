from typing import Any

from database.ckan_client import get_ckan_resources

from .config import DATASET_SINCE_2025_NAME, DELAY_DATA_FORMATS


def get_ttc_delays_dataset_resources() -> list[dict[str, Any]]:
    resources = [r for r in get_ckan_resources() if _is_delay_data_resource(r)]

    print("TTC delay data resources retrieved!\n")
    return resources


def _is_delay_data_resource(resource: dict[str, Any]) -> bool:
    name = resource.get("name", "")

    is_data_file = resource.get("format", "").upper() in DELAY_DATA_FORMATS
    is_dated_delay_file = "ttc-subway-delay" in name.lower() and "20" in name
    is_since_2025_file = name == DATASET_SINCE_2025_NAME

    return is_data_file and (is_dated_delay_file or is_since_2025_file)
