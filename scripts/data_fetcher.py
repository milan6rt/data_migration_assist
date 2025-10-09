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
    elif source == 'fabric':
        query = f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = '{schema}'
        ORDER BY TABLE_NAME
        """
        return pd.read_sql(query, conn)['TABLE_NAME'].tolist()

def get_table_row_count(conn, table_name, source='postgresql', schema='public'):
    if source == 'postgresql':
        query = f'SELECT COUNT(*) AS "count" FROM {schema}."{table_name}"'
        return pd.read_sql(query, conn)['count'].iloc[0]
    elif source == 'snowflake':
        # Snowflake uses uppercase identifiers without quotes
        query = f'SELECT COUNT(*) AS "count" FROM {schema.upper()}.{table_name.upper()}'
        return pd.read_sql(query, conn)['count'].iloc[0]
    elif source == 'fabric':
        # Fabric uses SQL Server syntax with brackets for identifiers
        query = f'SELECT COUNT(*) AS "count" FROM [{schema}].[{table_name}]'
        return pd.read_sql(query, conn)['count'].iloc[0]
    else:
        raise ValueError("Unsupported source. Use 'postgresql', 'snowflake', or 'fabric'.")

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
    elif source == 'fabric':
        query = f"""
        SELECT UPPER(COLUMN_NAME) AS COLUMN_NAME, UPPER(DATA_TYPE) AS DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
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
    elif source == 'fabric':
        # Fabric uses SQL Server syntax with TOP instead of LIMIT
        query = f'SELECT TOP {n} * FROM [{schema}].[{table_name}]'
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

# Fabric-specific functions
def get_fabric_databases(conn):
    """Get list of databases from Fabric"""
    query = "SELECT name FROM sys.databases WHERE database_id > 4 ORDER BY name"
    df = pd.read_sql(query, conn)
    return df['name'].tolist()

def get_fabric_schemas(conn):
    """Get list of schemas from Fabric"""
    query = """
        SELECT SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE SCHEMA_NAME NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest', 'db_owner', 'db_accessadmin',
                                    'db_securityadmin', 'db_ddladmin', 'db_backupoperator', 'db_datareader',
                                    'db_datawriter', 'db_denydatareader', 'db_denydatawriter')
        ORDER BY SCHEMA_NAME
    """
    df = pd.read_sql(query, conn)
    return df['SCHEMA_NAME'].tolist()
