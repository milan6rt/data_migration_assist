import snowflake.connector
import os
from dotenv import load_dotenv

# Load target database credentials from credentials/.env.target
load_dotenv('credentials/.env.target')

def get_snowflake_connection(database=None, schema=None):
    """
    Returns a connection to the target Snowflake database (cloud).

    Parameters:
    - database (str): Optional. If provided, connects to that specific database.
    - schema (str): Optional. If provided, uses that specific schema.

    Environment Variables Required (from credentials/.env.target):
    - SNOWFLAKE_USER (required)
    - SNOWFLAKE_PASSWORD (required)
    - SNOWFLAKE_ACCOUNT (required)
    - SNOWFLAKE_WAREHOUSE (required)
    - SNOWFLAKE_DATABASE (optional)
    - SNOWFLAKE_SCHEMA (optional)
    """
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    default_database = os.getenv("SNOWFLAKE_DATABASE")
    default_schema = os.getenv("SNOWFLAKE_SCHEMA")

    if not all([user, password, account, warehouse]):
        raise ValueError("Snowflake credentials not found. Please ensure credentials/.env.target file exists with required variables.")

    return snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database or default_database,
        schema=schema or default_schema
    )
