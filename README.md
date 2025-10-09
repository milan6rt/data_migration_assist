# Data Migration Quality Check Tool

A Streamlit-based application for comparing data quality between databases during cloud migration projects. Supports PostgreSQL, Microsoft Fabric, and Snowflake.

## Features

✅ **Flexible Source Selection** - Choose PostgreSQL or Microsoft Fabric as source
✅ **Flexible Target Selection** - Choose Snowflake or Microsoft Fabric as target
✅ **Database & Schema Selection** - Independent selection for all databases
✅ **Table Comparison** - Identify common tables and schema differences
✅ **Row Count Validation** - Ensure data completeness
✅ **Schema Structure Comparison** - Verify column counts and data types
✅ **Data Quality Checks** - Detect duplicates and null values
✅ **Sample Data Review** - Side-by-side data comparison
✅ **Excel Reports** - Export comprehensive comparison reports

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd data_migration_assist
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

**Source Database (PostgreSQL):**
```bash
cp credentials/.env.source.example credentials/.env.source
# Edit credentials/.env.source with your PostgreSQL credentials
```

**Target Database (Snowflake):**
```bash
cp credentials/.env.target.example credentials/.env.target
# Edit credentials/.env.target with your Snowflake credentials
```

**Microsoft Fabric (Source or Target):**
```bash
cp credentials/.env.fabric.example credentials/.env.fabric
# Edit credentials/.env.fabric with your Fabric credentials
```

### 4. Set Up Test Data
```bash
# PostgreSQL
psql -U your_username -h localhost -d migration_test_db -f scripts/setup_postgresql.sql

# Snowflake
# Run scripts/setup_snowflake.sql in Snowflake UI
```

### 5. Run the Application
```bash
streamlit run app.py
```

Open your browser at http://localhost:8502

## Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Comprehensive setup instructions
- **[Quick Start](QUICK_START.md)** - 5-minute getting started guide

## Project Structure

```
data_migration_assist/
├── app.py                          # Main Streamlit application
├── config/
│   ├── postgresql_config.py        # PostgreSQL connection handler
│   ├── snowflake_config.py         # Snowflake connection handler
│   └── fabric_config.py            # Microsoft Fabric connection handler
├── scripts/
│   ├── comparator.py               # Row count comparison logic
│   ├── data_fetcher.py             # Data retrieval functions
│   ├── quality_checks.py           # Data quality validation
│   ├── setup_postgresql.sql        # PostgreSQL test data setup
│   └── setup_snowflake.sql         # Snowflake test data setup
├── credentials/
│   ├── .env.source.example         # Source (PostgreSQL) credentials template
│   ├── .env.target.example         # Target (Snowflake) credentials template
│   └── .env.fabric.example         # Microsoft Fabric credentials template
├── requirements.txt                # Python dependencies
├── SETUP_GUIDE.md                  # Detailed setup documentation
└── QUICK_START.md                  # Quick reference guide
```

## Use Cases

- **Pre-migration validation** - Ensure schemas match before migration
- **Post-migration verification** - Confirm data integrity after migration
- **Ongoing monitoring** - Regular data quality checks
- **Audit reporting** - Export comparison results for compliance

## Technology Stack

- **Frontend**: Streamlit
- **Databases**: PostgreSQL, Microsoft Fabric, Snowflake
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Reporting**: XlsxWriter
- **Database Drivers**: psycopg2 (PostgreSQL), pyodbc (Fabric), snowflake-connector-python (Snowflake)

## Supported Comparison Scenarios

- **PostgreSQL → Snowflake** (original functionality)
- **PostgreSQL → Fabric** (new)
- **Fabric → Snowflake** (new)
- **Fabric → Fabric** (new, compare across Fabric databases)

## Security Notes

⚠️ **Never commit credentials to version control**

- `credentials/.env.source` - Contains source (PostgreSQL) credentials (gitignored)
- `credentials/.env.target` - Contains target (Snowflake) credentials (gitignored)
- `credentials/.env.fabric` - Contains Microsoft Fabric credentials (gitignored)
- Use the `.example` files as templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for internal use and cloud migration projects.

## Support

For issues or questions, please refer to:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions
- [QUICK_START.md](QUICK_START.md) for quick reference

---

**Last Updated**: October 2025
**Version**: 2.0
