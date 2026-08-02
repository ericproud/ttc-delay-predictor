import psycopg

from database.config import SUPABASE_DB_URI


def get_connection() -> psycopg.Connection:
    return psycopg.connect(SUPABASE_DB_URI)
