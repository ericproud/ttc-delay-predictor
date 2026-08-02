import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_DB_URI = os.environ["SUPABASE_DB_URI"]

CKAN_PACKAGE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
DATASET_ID = "ttc-subway-delay-data"
