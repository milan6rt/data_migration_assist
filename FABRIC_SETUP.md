# Microsoft Fabric Setup Guide

This guide explains how to configure Microsoft Fabric connectivity for the Data Migration Assist tool.

## Prerequisites

1. **ODBC Driver 18 for SQL Server** installed on your system
   - **macOS**: `brew install unixodbc freetds`
   - **Windows**: Download from [Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - **Linux**: `sudo apt-get install unixodbc-dev` or `sudo yum install unixODBC-devel`

2. **Python packages**:
   ```bash
   pip install pyodbc python-dotenv pandas
   ```

3. **Azure Service Principal** with access to your Fabric workspace

## Azure Service Principal Setup

### 1. Create Service Principal

```bash
# Using Azure CLI
az login
az ad sp create-for-rbac --name "fabric-migration-app" --role Contributor
```

This will output:
```json
{
  "appId": "your-client-id",
  "displayName": "fabric-migration-app",
  "password": "your-client-secret",
  "tenant": "your-tenant-id"
}
```

### 2. Grant Fabric Permissions

1. Go to your **Fabric Workspace** in the Microsoft Fabric portal
2. Click **Workspace settings** → **Manage access**
3. Add the service principal with **Contributor** or **Admin** role
4. Ensure the service principal has access to the SQL Endpoint

## Configuration

### 1. Copy the Fabric Credentials Template

```bash
cp credentials/.env.fabric.example credentials/.env.fabric
```

### 2. Edit credentials/.env.fabric

```bash
# Microsoft Fabric SQL Connection Credentials

# Azure AD credentials
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Fabric SQL Server endpoint (format: servername.datawarehouse.fabric.microsoft.com,1433)
FABRIC_SQL_SERVER=your-workspace-id.datawarehouse.fabric.microsoft.com,1433

# Default database
FABRIC_SQL_DATABASE=your-database-name

# Optional: Fabric Workspace details (for reference)
WORKSPACE_ID=your-workspace-id
ITEM_ID=your-item-id
LAKEHOUSE_ID=your-lakehouse-id
LAKEHOUSE_NAME=your-lakehouse-name
```

### 3. Find Your Fabric SQL Endpoint

1. Open **Microsoft Fabric** portal
2. Navigate to your **Workspace**
3. Open your **Data Warehouse** or **SQL Endpoint**
4. Click **Settings** → **Connection strings**
5. Copy the **SQL connection string** - it will look like:
   ```
   servername.datawarehouse.fabric.microsoft.com,1433
   ```

## Testing the Connection

### Test Script

Create a test file `test_fabric_conn.py`:

```python
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv('credentials/.env.fabric')

SERVER = os.getenv("FABRIC_SQL_SERVER")
DATABASE = os.getenv("FABRIC_SQL_DATABASE")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server={SERVER};"
    f"Database={DATABASE};"
    "Authentication=ActiveDirectoryServicePrincipal;"
    f"UID={CLIENT_ID};PWD={CLIENT_SECRET};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

try:
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT TOP 5 name, create_date FROM sys.objects ORDER BY create_date DESC;")
            print("✅ Connection successful!")
            for row in cur.fetchall():
                print(row)
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run the test:
```bash
python3 test_fabric_conn.py
```

## Usage in the Application

### 1. Launch the Application

```bash
streamlit run app.py
```

### 2. Select Source/Target Database

In the sidebar:
- **Source Database**: Select "Fabric" to use Fabric as source
- **Target Database**: Select "Fabric" to use Fabric as target

### 3. Select Database and Schema

- Choose your **Fabric Database**
- Select the **Schema** (usually `dbo`)
- Pick a **Table** to compare

## Comparison Scenarios

### PostgreSQL → Fabric
Compare on-premises PostgreSQL data with Microsoft Fabric:
- Source: PostgreSQL
- Target: Fabric

### Fabric → Snowflake
Validate data migration from Fabric to Snowflake:
- Source: Fabric
- Target: Snowflake

### Fabric → Fabric
Compare data across different Fabric databases or workspaces:
- Source: Fabric (Database A)
- Target: Fabric (Database B)

## Troubleshooting

### Error: "Driver not found"

**Solution**: Install ODBC Driver 18 for SQL Server
```bash
# macOS
brew install unixodbc freetds

# Check installed drivers
odbcinst -q -d
```

### Error: "Login failed for user"

**Solution**:
1. Verify service principal has correct permissions in Fabric workspace
2. Check that AZURE_CLIENT_ID and AZURE_CLIENT_SECRET are correct
3. Ensure the service principal has **Contributor** or **Admin** role

### Error: "Cannot connect to server"

**Solution**:
1. Verify FABRIC_SQL_SERVER is correct (should end with `.datawarehouse.fabric.microsoft.com,1433`)
2. Check network connectivity
3. Ensure firewall allows outbound connections on port 1433

### Error: "Database does not exist"

**Solution**:
1. Verify FABRIC_SQL_DATABASE name matches your Fabric database
2. Ensure the service principal has access to the specific database
3. Check that the database is in the correct workspace

## Security Best Practices

1. **Never commit credentials**: The `.env.fabric` file is in `.gitignore`
2. **Rotate secrets regularly**: Update service principal secrets periodically
3. **Use least privilege**: Grant only necessary permissions to the service principal
4. **Monitor access**: Review Fabric workspace access logs regularly

## Additional Resources

- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Azure Service Principal Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
- [ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

**Last Updated**: October 2025
