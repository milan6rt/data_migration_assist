# Data Migration Quality Check - Setup Guide

## Overview
This guide provides step-by-step instructions to set up identical test environments in both PostgreSQL (on-premises) and Snowflake (cloud) for apple-to-apple comparison during cloud data migration.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [PostgreSQL Setup](#postgresql-setup)
3. [Snowflake Setup](#snowflake-setup)
4. [Verification Steps](#verification-steps)
5. [Running the Comparison App](#running-the-comparison-app)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- PostgreSQL 12+ installed locally
- Access to Snowflake account
- Python 3.9+
- Terminal/Command Line access

### Required Credentials

**Source Database (PostgreSQL):**
Set up environment variables (copy `credentials/.env.source.example` to `credentials/.env.source` and fill in your credentials):
```bash
cp credentials/.env.source.example credentials/.env.source
```
Then edit `credentials/.env.source`:
```
PG_HOST=localhost
PG_USER=your_username
PG_PASSWORD=your_password
PG_PORT=5432
```

**Target Database (Snowflake):**
Copy the example file and fill in your credentials:
```bash
cp credentials/.env.target.example credentials/.env.target
```
Then edit `credentials/.env.target`:
```
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=your_schema_name
```

---

## PostgreSQL Setup

### Step 1: Connect to PostgreSQL
Open your terminal and connect to PostgreSQL:

```bash
psql -U milan -h localhost
```

### Step 2: Create Database
Run the following command in psql:

```sql
CREATE DATABASE migration_test_db;
```

### Step 3: Run Setup Script
You have two options to run the setup script:

**Option A: Using psql command line**
```bash
psql -U milan -h localhost -d migration_test_db -f scripts/setup_postgresql.sql
```

**Option B: Using psql interactive mode**
```bash
psql -U milan -h localhost -d migration_test_db
```
Then inside psql:
```sql
\i scripts/setup_postgresql.sql
```

### Step 4: Verify PostgreSQL Setup
Check that all tables were created:

```sql
\c migration_test_db

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'test_schema'
ORDER BY tablename;
```

Verify row counts:

```sql
SELECT 'customers' as table_name, COUNT(*) as row_count FROM test_schema.customers
UNION ALL
SELECT 'accounts', COUNT(*) FROM test_schema.accounts
UNION ALL
SELECT 'transactions', COUNT(*) FROM test_schema.transactions
UNION ALL
SELECT 'loans', COUNT(*) FROM test_schema.loans;
```

**Expected Output:**
```
  table_name   | row_count
---------------+-----------
 customers     |        40
 accounts      |        40
 transactions  |        50
 loans         |        30
```

---

## Snowflake Setup

### Step 1: Access Snowflake Web UI
1. Navigate to: https://app.snowflake.com/mzcjjpk/rs71431/
2. Login with your credentials
3. Select the appropriate role (ACCOUNTADMIN or SYSADMIN recommended)

### Step 2: Open Worksheet
1. Click on "Worksheets" in the left navigation
2. Click "+ Worksheet" to create a new worksheet

### Step 3: Run Setup Script

**Option A: Copy and Paste**
1. Open `scripts/setup_snowflake.sql` in a text editor
2. Copy all contents
3. Paste into Snowflake worksheet
4. Click "Run All" button (or press Ctrl+Enter)

**Option B: Upload File**
1. In Snowflake worksheet, click the three dots (⋮) menu
2. Select "Import SQL from file"
3. Choose `scripts/setup_snowflake.sql`
4. Click "Run All"

### Step 4: Verify Snowflake Setup
Run the following queries in Snowflake:

```sql
-- Switch to the database
USE DATABASE MIGRATION_TEST_DB;
USE SCHEMA TEST_SCHEMA;

-- List all tables
SHOW TABLES IN SCHEMA TEST_SCHEMA;

-- Verify row counts
SELECT 'CUSTOMERS' as TABLE_NAME, COUNT(*) as ROW_COUNT FROM CUSTOMERS
UNION ALL
SELECT 'ACCOUNTS', COUNT(*) FROM ACCOUNTS
UNION ALL
SELECT 'TRANSACTIONS', COUNT(*) FROM TRANSACTIONS
UNION ALL
SELECT 'LOANS', COUNT(*) FROM LOANS;
```

**Expected Output:**
```
TABLE_NAME    | ROW_COUNT
--------------+-----------
CUSTOMERS     |        40
ACCOUNTS      |        40
TRANSACTIONS  |        50
LOANS         |        30
```

---

## Verification Steps

### Data Integrity Checks

Run these queries in both PostgreSQL and Snowflake to ensure data consistency:

#### PostgreSQL:
```sql
-- Check primary keys
SELECT 'customers' as table_name, MIN(customer_id) as min_id, MAX(customer_id) as max_id FROM test_schema.customers
UNION ALL
SELECT 'accounts', MIN(account_id), MAX(account_id) FROM test_schema.accounts
UNION ALL
SELECT 'transactions', MIN(transaction_id), MAX(transaction_id) FROM test_schema.transactions
UNION ALL
SELECT 'loans', MIN(loan_id), MAX(loan_id) FROM test_schema.loans;

-- Sample data from each table
SELECT * FROM test_schema.customers LIMIT 3;
SELECT * FROM test_schema.accounts LIMIT 3;
```

#### Snowflake:
```sql
-- Check primary keys
SELECT 'CUSTOMERS' as TABLE_NAME, MIN(CUSTOMER_ID) as MIN_ID, MAX(CUSTOMER_ID) as MAX_ID FROM CUSTOMERS
UNION ALL
SELECT 'ACCOUNTS', MIN(ACCOUNT_ID), MAX(ACCOUNT_ID) FROM ACCOUNTS
UNION ALL
SELECT 'TRANSACTIONS', MIN(TRANSACTION_ID), MAX(TRANSACTION_ID) FROM TRANSACTIONS
UNION ALL
SELECT 'LOANS', MIN(LOAN_ID), MAX(LOAN_ID) FROM LOANS;

-- Sample data from each table
SELECT * FROM CUSTOMERS LIMIT 3;
SELECT * FROM ACCOUNTS LIMIT 3;
```

### Expected Results (Both Systems)
| table_name   | min_id | max_id |
|--------------|--------|--------|
| customers    | 1      | 40     |
| accounts     | 101    | 140    |
| transactions | 1001   | 1050   |
| loans        | 2001   | 2030   |

---

## Running the Comparison App

### Step 1: Ensure Dependencies are Installed
```bash
cd /Users/milan/Documents/data_migration_assist
pip3 install -r requirements.txt
```

### Step 2: Verify Configuration Files

**Check Source Credentials:**
```bash
cat credentials/.env.source
```

**Check Target Credentials:**
```bash
cat credentials/.env.target
```

### Step 3: Start the Streamlit App
```bash
streamlit run app.py
```

Or if already running:
```bash
python3 -m streamlit run app.py
```

The app will open at: http://localhost:8502

### Step 4: Use the App for Comparison

1. **Select PostgreSQL Database**: Choose `migration_test_db`
2. **Select PostgreSQL Schema**: Choose `test_schema`
3. **Select Snowflake Database**: Choose `MIGRATION_TEST_DB`
4. **Select Snowflake Schema**: Choose `TEST_SCHEMA`
5. **Select Table**: Choose any table (e.g., `customers`, `accounts`, `transactions`, `loans`)

### Step 5: Review Comparison Results

The app will display:
- ✅ **Row Count Comparison**: Ensures both databases have the same number of records
- ✅ **Column Count Comparison**: Verifies schema structure matches
- ✅ **Sample Data Comparison**: Shows side-by-side data from both systems
- ✅ **Data Quality Checks**:
  - Duplicate row detection
  - Null value percentages per column
- ✅ **Summary Report**: Consolidated view of all checks

### Step 6: Generate Full Summary Report

1. Click "📋 Generate Full Summary Report" in the sidebar
2. Review the comprehensive comparison for all tables
3. Click "📅 Download Full Summary Report (Excel)" to export results

---

## Troubleshooting

### PostgreSQL Issues

**Problem: "database does not exist"**
```sql
-- List all databases
\l

-- Create database if missing
CREATE DATABASE migration_test_db;
```

**Problem: "schema does not exist"**
```sql
-- Connect to database first
\c migration_test_db

-- List all schemas
\dn

-- Create schema if missing
CREATE SCHEMA IF NOT EXISTS test_schema;
```

**Problem: "permission denied"**
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE migration_test_db TO milan;
GRANT ALL PRIVILEGES ON SCHEMA test_schema TO milan;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_schema TO milan;
```

**Problem: "relation already exists"**
If tables already exist and you want to recreate them:
```sql
-- Drop schema and all tables
DROP SCHEMA IF EXISTS test_schema CASCADE;

-- Then re-run setup script
\i scripts/setup_postgresql.sql
```

### Snowflake Issues

**Problem: "Object does not exist"**
```sql
-- Check current database and schema
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();

-- List all databases
SHOW DATABASES;

-- Switch to correct database
USE DATABASE MIGRATION_TEST_DB;
USE SCHEMA TEST_SCHEMA;
```

**Problem: "Insufficient privileges"**
```sql
-- Check your current role
SELECT CURRENT_ROLE();

-- Switch to a role with appropriate privileges
USE ROLE ACCOUNTADMIN;
-- or
USE ROLE SYSADMIN;
```

**Problem: "Table already exists"**
If tables already exist and you want to recreate them:
```sql
-- Drop database and all objects
DROP DATABASE IF EXISTS MIGRATION_TEST_DB CASCADE;

-- Then re-run setup script
```

**Problem: "SQL compilation error"**
- Ensure you're running the entire script, not individual lines
- Check that foreign key references are created in the correct order
- Verify that the COMPUTE_WH warehouse is running:
  ```sql
  SHOW WAREHOUSES;
  ALTER WAREHOUSE COMPUTE_WH RESUME;
  ```

### App Connection Issues

**Problem: "Connection refused" (PostgreSQL)**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL if needed (macOS)
brew services start postgresql

# Check connection manually
psql -U milan -h localhost -d migration_test_db
```

**Problem: "Snowflake connection error"**
1. Verify credentials in `.streamlit/secrets.toml`
2. Check account identifier is correct: `mzcjjpk-rs71431`
3. Ensure warehouse is running in Snowflake UI
4. Test connection using Python:
```python
import snowflake.connector
conn = snowflake.connector.connect(
    user='MShiksharthi',
    password='Milan@Delphi123',
    account='mzcjjpk-rs71431',
    warehouse='COMPUTE_WH',
    database='MIGRATION_TEST_DB',
    schema='TEST_SCHEMA'
)
print("Connected successfully!")
conn.close()
```

**Problem: "Table not found in app"**
- Ensure you've selected the correct database and schema in both dropdowns
- Refresh the app (Streamlit auto-reloads, or press 'R' in browser)
- Verify tables exist using the verification queries above

---

## Data Schema Details

### Tables Overview

| Table Name   | Rows | Description |
|--------------|------|-------------|
| CUSTOMERS    | 40   | Customer master data with contact info |
| ACCOUNTS     | 40   | Bank accounts linked to customers |
| TRANSACTIONS | 50   | Account transactions (debits/credits) |
| LOANS        | 30   | Customer loan information |

### Table Structures

#### CUSTOMERS / customers
```
CUSTOMER_ID (INTEGER, PK)
NAME (VARCHAR(100), NOT NULL)
EMAIL (VARCHAR(100))
PHONE (VARCHAR(20))
```

#### ACCOUNTS / accounts
```
ACCOUNT_ID (INTEGER, PK)
CUSTOMER_ID (INTEGER, FK → CUSTOMERS)
ACCOUNT_TYPE (VARCHAR(50))
BALANCE (NUMBER(12,2))
```

#### TRANSACTIONS / transactions
```
TRANSACTION_ID (INTEGER, PK)
ACCOUNT_ID (INTEGER, FK → ACCOUNTS)
TRANSACTION_DATE (DATE)
AMOUNT (NUMBER(12,2))
TYPE (VARCHAR(20))
```

#### LOANS / loans
```
LOAN_ID (INTEGER, PK)
CUSTOMER_ID (INTEGER, FK → CUSTOMERS)
LOAN_AMOUNT (NUMBER(12,2))
INTEREST_RATE (NUMBER(4,2))
START_DATE (DATE)
END_DATE (DATE)
```

---

## Key Differences: PostgreSQL vs Snowflake

### Naming Conventions
- **PostgreSQL**: Uses lowercase identifiers by default (`customers`, `customer_id`)
- **Snowflake**: Uses uppercase identifiers by default (`CUSTOMERS`, `CUSTOMER_ID`)

### Data Types
- **PostgreSQL**: `VARCHAR`, `INTEGER`, `NUMERIC`, `DATE`
- **Snowflake**: `VARCHAR`, `INTEGER`, `NUMBER`, `DATE`

### Schema Qualification
- **PostgreSQL**: `schema_name.table_name` (e.g., `test_schema.customers`)
- **Snowflake**: `SCHEMA_NAME.TABLE_NAME` (e.g., `TEST_SCHEMA.CUSTOMERS`)

The comparison app automatically handles these differences to ensure accurate apple-to-apple comparison.

---

## Cleanup (Optional)

### Remove PostgreSQL Test Data
```sql
-- Connect to postgres database
\c postgres

-- Drop test database
DROP DATABASE IF EXISTS migration_test_db;
```

### Remove Snowflake Test Data
```sql
-- Drop test database
DROP DATABASE IF EXISTS MIGRATION_TEST_DB;
```

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error messages in the Streamlit app
3. Verify connection credentials in config files
4. Ensure both database systems are accessible

---

## Best Practices for Cloud Migration

1. **Always test with sample data first** (as done in this setup)
2. **Verify row counts match** before and after migration
3. **Check data types compatibility** between source and target
4. **Monitor null value percentages** to ensure data quality
5. **Validate foreign key relationships** are maintained
6. **Generate and archive comparison reports** for audit trail
7. **Test with production-like data volumes** before actual migration

---

## Next Steps

After completing this setup:
1. ✅ Run the comparison app to familiarize yourself with the interface
2. ✅ Generate a full summary report to understand the reporting format
3. ✅ Modify table structures to test edge cases (optional)
4. ✅ Prepare your actual production data for migration
5. ✅ Update connection credentials for production systems
6. ✅ Schedule regular comparison runs during migration

---

**Document Version**: 1.0
**Last Updated**: 2025-10-07
**Compatible With**: PostgreSQL 12+, Snowflake Enterprise Edition
