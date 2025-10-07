# Quick Start Guide - Data Migration Testing

## 🚀 5-Minute Setup

### PostgreSQL Setup (2 minutes)
```bash
# 1. Connect to PostgreSQL
psql -U milan -h localhost

# 2. Create database
CREATE DATABASE migration_test_db;
\q

# 3. Run setup script
psql -U milan -h localhost -d migration_test_db -f scripts/setup_postgresql.sql
```

### Snowflake Setup (2 minutes)
```sql
-- 1. Login to Snowflake at: https://app.snowflake.com/mzcjjpk/rs71431/

-- 2. Open a new worksheet and run:
-- (Copy entire contents of scripts/setup_snowflake.sql and paste)
```

### Run Comparison App (1 minute)
```bash
# Start the app
streamlit run app.py

# Open browser: http://localhost:8502
# Select databases, schemas, and tables to compare
```

---

## 📋 Quick Reference Commands

### PostgreSQL Commands
```bash
# Connect
psql -U milan -h localhost -d migration_test_db

# Verify data
SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'test_schema';

# Row counts
SELECT 'customers' as table_name, COUNT(*) FROM test_schema.customers
UNION ALL SELECT 'accounts', COUNT(*) FROM test_schema.accounts
UNION ALL SELECT 'transactions', COUNT(*) FROM test_schema.transactions
UNION ALL SELECT 'loans', COUNT(*) FROM test_schema.loans;
```

### Snowflake Commands
```sql
-- Switch context
USE DATABASE MIGRATION_TEST_DB;
USE SCHEMA TEST_SCHEMA;

-- Verify data
SHOW TABLES;

-- Row counts
SELECT 'CUSTOMERS' as TABLE_NAME, COUNT(*) FROM CUSTOMERS
UNION ALL SELECT 'ACCOUNTS', COUNT(*) FROM ACCOUNTS
UNION ALL SELECT 'TRANSACTIONS', COUNT(*) FROM TRANSACTIONS
UNION ALL SELECT 'LOANS', COUNT(*) FROM LOANS;
```

---

## ✅ Expected Results

All queries should return:
- **customers/CUSTOMERS**: 40 rows
- **accounts/ACCOUNTS**: 40 rows
- **transactions/TRANSACTIONS**: 50 rows
- **loans/LOANS**: 30 rows

---

## 🔧 Quick Fixes

### PostgreSQL not connecting?
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Restart PostgreSQL (macOS)
brew services restart postgresql
```

### Snowflake connection error?
1. Check warehouse is running: `ALTER WAREHOUSE COMPUTE_WH RESUME;`
2. Verify credentials in `credentials/.env.target`
3. Ensure all required environment variables are set

### Tables not showing in app?
1. Refresh browser (press 'R')
2. Verify database and schema selections match
3. Check tables exist using verification queries above

---

## 📊 What Gets Compared?

✅ Row counts
✅ Column counts
✅ Data types
✅ Sample data (120 rows)
✅ Duplicate records
✅ Null value percentages
✅ Schema structures

---

## 📥 Download Options

- **Single Table Report**: Compare one table at a time
- **Full Schema Report**: Excel file with all tables (click "Generate Full Summary Report")

---

## 🎯 Use Cases

1. **Pre-migration validation**: Ensure schemas match
2. **Post-migration verification**: Confirm data integrity
3. **Ongoing monitoring**: Regular data quality checks
4. **Audit reporting**: Export comparison results

---

## 📞 Need Help?

See full documentation: `SETUP_GUIDE.md`
