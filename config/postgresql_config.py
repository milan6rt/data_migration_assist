import psycopg2
import os
from dotenv import load_dotenv

# Load source database credentials from credentials/.env.source
load_dotenv('credentials/.env.source')

def get_postgresql_connection(database=None):
    """
    Returns a connection to the source PostgreSQL database (on-premises).

    Parameters:
    - database (str): Optional. If provided, connects to that specific database.

    Environment Variables Required (from credentials/.env.source):
    - PG_HOST (default: localhost)
    - PG_USER (required)
    - PG_PASSWORD (required)
    - PG_PORT (default: 5432)
    """
    host = os.getenv("PG_HOST", "localhost")
    user = os.getenv("PG_USER")
    password = os.getenv("PG_PASSWORD")
    port = int(os.getenv("PG_PORT", "5432"))

    if not user or not password:
        raise ValueError("PostgreSQL credentials not found. Please ensure credentials/.env.source file exists with PG_USER and PG_PASSWORD.")

    if database:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
    else:
        # Default to postgres system database if no DB specified
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database="postgres",
            port=port
        )

    return conn
