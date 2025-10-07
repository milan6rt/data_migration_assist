import pandas as pd

def get_postgresql_databases(conn):
    query = "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres'"
    return pd.read_sql(query, conn)['datname'].tolist()

def get_postgresql_schemas(conn):
    query = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
    """
    return pd.read_sql(query, conn)['schema_name'].tolist()

def get_table_list(conn, source='postgresql', schema='public'):
    if source == 'postgresql':
        query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' AND table_schema = '{schema}'
        ORDER BY table_name
        """
        return pd.read_sql(query, conn)['table_name'].tolist()
    elif source == 'snowflake':
        query = f"SHOW TABLES IN SCHEMA {schema}"
        return pd.read_sql(query, conn)['name'].tolist()

def get_table_row_count(conn, table_name, source='postgresql', schema='public'):
    if source == 'postgresql':
        query = f'SELECT COUNT(*) AS "count" FROM {schema}."{table_name}"'
        return pd.read_sql(query, conn)['count'].iloc[0]
    elif source == 'snowflake':
        # Snowflake uses uppercase identifiers without quotes
        query = f'SELECT COUNT(*) AS "count" FROM {schema.upper()}.{table_name.upper()}'
        return pd.read_sql(query, conn)['count'].iloc[0]
    else:
        raise ValueError("Unsupported source. Use 'postgresql' or 'snowflake'.")

def get_table_schema(conn, table_name, source='postgresql', schema='public'):
    if source == 'postgresql':
        query = f"""
        SELECT UPPER(column_name) AS column_name, UPPER(data_type) AS data_type
        FROM information_schema.columns
        WHERE table_schema = '{schema}' AND table_name = '{table_name}'
        ORDER BY column_name
        """
    elif source == 'snowflake':
        query = f"""
        SELECT UPPER(COLUMN_NAME) AS COLUMN_NAME, UPPER(DATA_TYPE) AS DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema.upper()}' AND TABLE_NAME = '{table_name.upper()}'
        ORDER BY COLUMN_NAME
        """
    else:
        raise ValueError("Unsupported source type.")

    return pd.read_sql(query, conn)

def get_sample_data(conn, table_name, n=100, source='postgresql', schema='public'):
    if source == 'postgresql':
        query = f'SELECT * FROM {schema}."{table_name}" LIMIT {n}'
    elif source == 'snowflake':
        # Snowflake uses uppercase identifiers without quotes
        query = f"SELECT * FROM {schema.upper()}.{table_name.upper()} LIMIT {n}"
    return pd.read_sql(query, conn)

# scripts/data_fetcher.py

def get_snowflake_databases(conn):
    query = "SHOW DATABASES"
    df = pd.read_sql(query, conn)
    return df['name'].tolist()

def get_snowflake_schemas(conn):
    query = "SHOW SCHEMAS"
    df = pd.read_sql(query, conn)
    return df['name'].tolist()
