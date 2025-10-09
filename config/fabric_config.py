import pyodbc
import os
from dotenv import load_dotenv

# Load Fabric credentials from credentials/.env.fabric
load_dotenv('credentials/.env.fabric')

def get_fabric_connection(database=None):
    """
    Returns a connection to Microsoft Fabric SQL database.

    Parameters:
    - database (str): Optional. If provided, connects to that specific database.

    Environment Variables Required (from credentials/.env.fabric):
    - FABRIC_SQL_SERVER (required)
    - FABRIC_SQL_DATABASE (required)
    - AZURE_CLIENT_ID (required)
    - AZURE_CLIENT_SECRET (required)
    """
    server = os.getenv("FABRIC_SQL_SERVER")
    default_database = os.getenv("FABRIC_SQL_DATABASE")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([server, default_database, client_id, client_secret]):
        raise ValueError("Fabric credentials not found. Please ensure credentials/.env.fabric file exists with required variables.")

    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={server};"
        f"Database={database or default_database};"
        "Authentication=ActiveDirectoryServicePrincipal;"
        f"UID={client_id};PWD={client_secret};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

    return pyodbc.connect(conn_str)
