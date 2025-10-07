import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Import our modules
# Note: Credentials are loaded in their respective config files
# - Source (PostgreSQL): config/postgresql_config.py loads from credentials/.env.source
# - Target (Snowflake): config/snowflake_config.py loads from credentials/.env.target
from config.postgresql_config import get_postgresql_connection
from config.snowflake_config import get_snowflake_connection
from scripts import data_fetcher, comparator, quality_checks

# Title and description
st.title("Data Migration Assist")
st.markdown("This app compares table data between the source (PostgreSQL) and target (Snowflake) databases during cloud migration.")

# Sidebar: Database and Schema Selection
with st.sidebar:
    st.image("Logo1.png", width=120)
    st.markdown("---")

    # PostgreSQL Connection Section
    st.markdown("## 🔍 PostgreSQL Connection")

    # Fetch all PostgreSQL databases
    conn_master = get_postgresql_connection(database="postgres")
    pg_db_list = data_fetcher.get_postgresql_databases(conn_master)
    conn_master.close()

    selected_pg_db = st.selectbox("Select PostgreSQL Database", pg_db_list, key="pg_db")

    # Connect to selected PostgreSQL database
    conn_postgresql = get_postgresql_connection(database=selected_pg_db)

    # Fetch schemas for selected PostgreSQL database
    pg_schemas = data_fetcher.get_postgresql_schemas(conn_postgresql)
    selected_pg_schema = st.selectbox("Select PostgreSQL Schema", pg_schemas, key="pg_schema")

    # Fetch tables for selected PostgreSQL schema
    tables_postgresql = data_fetcher.get_table_list(conn_postgresql, source='postgresql', schema=selected_pg_schema)

    st.markdown("---")

    # Snowflake Connection Section
    st.markdown("## ❄️ Snowflake Connection")

    conn_snowflake = None
    sf_db_list = []
    sf_schemas = []
    tables_snowflake = []

    try:
        # Initial Snowflake connection to fetch databases
        conn_snowflake_temp = get_snowflake_connection()
        sf_db_list = data_fetcher.get_snowflake_databases(conn_snowflake_temp)
        conn_snowflake_temp.close()

        selected_sf_db = st.selectbox("Select Snowflake Database", sf_db_list, key="sf_db")

        # Connect to selected Snowflake database
        conn_snowflake = get_snowflake_connection(database=selected_sf_db)

        # Fetch schemas for selected Snowflake database
        sf_schemas = data_fetcher.get_snowflake_schemas(conn_snowflake)
        selected_sf_schema = st.selectbox("Select Snowflake Schema", sf_schemas, key="sf_schema")

        # Fetch tables for selected Snowflake schema
        tables_snowflake = data_fetcher.get_table_list(conn_snowflake, source='snowflake', schema=selected_sf_schema)

    except Exception as e:
        st.warning(f"Snowflake connection error: {e}")
        selected_sf_schema = None

    st.markdown("---")

    # Table Selection (from PostgreSQL tables)
    st.markdown("## 📊 Table Selection")
    selected_table = st.selectbox("Select a Table to Compare", tables_postgresql, key="table_select")

    st.markdown("---")

    # Sidebar button to trigger full summary generation
    if st.button("📋 Generate Full Summary Report"):
        st.session_state.generate_summary = True
    else:
        st.session_state.generate_summary = False

# --- Table Comparison Section ---
st.markdown("---")
st.markdown("### 📁 Table Presence Comparison")

# Case-insensitive comparison for table names
# PostgreSQL uses lowercase, Snowflake uses uppercase
tables_postgresql_upper = [t.upper() for t in tables_postgresql]
tables_snowflake_upper = [t.upper() for t in tables_snowflake]

# Find common tables (case-insensitive)
common_tables_upper = list(set(tables_postgresql_upper) & set(tables_snowflake_upper))
common_tables = [t for t in tables_postgresql if t.upper() in common_tables_upper]

# Find tables only in PostgreSQL (case-insensitive)
postgresql_only_upper = list(set(tables_postgresql_upper) - set(tables_snowflake_upper))
postgresql_only = [t for t in tables_postgresql if t.upper() in postgresql_only_upper]

# Find tables only in Snowflake (case-insensitive)
snowflake_only_upper = list(set(tables_snowflake_upper) - set(tables_postgresql_upper))
snowflake_only = [t for t in tables_snowflake if t.upper() in snowflake_only_upper]

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### ✅ Common Tables")
    st.write(common_tables)

with col2:
    st.markdown("#### ❌ Tables only in PostgreSQL")
    st.write(postgresql_only)
    st.markdown("#### ❌ Tables only in Snowflake")
    st.write(snowflake_only)

# --- Full Summary Section ---
if st.session_state.get("generate_summary", False):
    st.header("📄 Full Schema-Level Summary Report")
    output = BytesIO()
    with st.expander("Table's Summary"):
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for table in common_tables:
                # st.write(f"Processing: {table}")
                row_source = data_fetcher.get_table_row_count(conn_postgresql, table, 'postgresql', selected_pg_schema)
                row_target = data_fetcher.get_table_row_count(conn_snowflake, table, 'snowflake', selected_sf_schema)
                match, count_source, count_target = comparator.compare_row_counts(row_source, row_target)

                schema_source = data_fetcher.get_table_schema(conn_postgresql, table, 'postgresql', selected_pg_schema)
                schema_target = data_fetcher.get_table_schema(conn_snowflake, table, 'snowflake', selected_sf_schema)
                column_match = schema_source.shape[0] == schema_target.shape[0]

                sample_source = data_fetcher.get_sample_data(conn_postgresql, table, 120, 'postgresql', selected_pg_schema)
                sample_target = data_fetcher.get_sample_data(conn_snowflake, table, 120, 'snowflake', selected_sf_schema)
                dup_sql = quality_checks.check_duplicates(sample_source)
                dup_sf = quality_checks.check_duplicates(sample_target)
                null_sql = quality_checks.check_nulls(sample_source).round(0)
                null_sf = quality_checks.check_nulls(sample_target).round(0)

                null_sql.index = null_sql.index.str.upper()
                null_sf.index = null_sf.index.str.upper()
                null_df = pd.concat([null_sql, null_sf], axis=1).fillna(0)
                null_df.columns = ["PostgreSQL (%)", "Snowflake (%)"]
                null_df["Difference"] = (null_df["PostgreSQL (%)"] - null_df["Snowflake (%)"]).abs().astype(int)
                null_df = null_df.astype(int).reset_index().rename(columns={"index": "Column Name"})

                ## View Data
                st.markdown("---") 
                st.subheader(f"📊 Summary Report - {table}")

                sample_source = data_fetcher.get_sample_data(conn_postgresql, table, n=120, source='postgresql',schema=selected_pg_schema)
                sample_target = data_fetcher.get_sample_data(conn_snowflake, table, n=120, source='snowflake',schema=selected_sf_schema)
                duplicates_sql = quality_checks.check_duplicates(sample_source)
                duplicates_snowflake = quality_checks.check_duplicates(sample_target)

                summary_data = {
                    "Check": [
                        "Table Presence in Both DBs",
                        "Row Count Match",
                        "Column Count Match",
                        "Duplicate Rows (PostgreSQL)",
                        "Duplicate Rows (Snowflake)"
                    ],
                    "Result": [
                        "✅ Present in both" if table in common_tables else "❌ Missing in one",
                        "✅ Match" if match else "❌ Mismatch",
                        "✅ Match" if schema_source.shape[0] == schema_target.shape[0] else "❌ Mismatch",
                        f"{duplicates_sql} duplicates",
                        f"{duplicates_snowflake} duplicates"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)

                st.markdown("##### 🧪 Null Value Comparison (Source vs Target)")
                # Get null percentages and round to 0 decimals
                nulls_sqlserver = quality_checks.check_nulls(sample_source).round(0)
                nulls_snowflake = quality_checks.check_nulls(sample_target).round(0)

                    # Standardize column names to uppercase
                nulls_sqlserver.index = nulls_sqlserver.index.str.upper()
                nulls_snowflake.index = nulls_snowflake.index.str.upper()

                    # Combine and compare
                null_comparison = pd.concat([nulls_sqlserver, nulls_snowflake], axis=1)
                null_comparison.columns = ['PostgreSQL (%)', 'Snowflake (%)']

                    # Replace NaN with 0 before calculating difference
                null_comparison.fillna(0, inplace=True)

                    # Calculate and cast
                null_comparison['Difference'] = (null_comparison['PostgreSQL (%)'] - null_comparison['Snowflake (%)']).abs().astype(int)
                null_comparison[['PostgreSQL (%)', 'Snowflake (%)']] = null_comparison[['PostgreSQL (%)', 'Snowflake (%)']].astype(int)

                    # Prepare for display
                null_comparison.reset_index(inplace=True)
                null_comparison.rename(columns={'index': 'Column Name'}, inplace=True)

                    # Highlight differences
                def highlight_diff(val):
                    return 'background-color: red' if val > 0 else ''

                # Display with highlighting
                st.dataframe(null_comparison.style.applymap(highlight_diff, subset=['Difference']), use_container_width=True)

                summary_df = pd.DataFrame({
                    "Metric": [
                        "Row Count Source", "Row Count Target", "Row Count Match",
                        "Column Count Match", "Duplicates PostgreSQL", "Duplicates Snowflake"
                    ],
                    "Value": [
                        count_source, count_target, match, column_match, dup_sql, dup_sf
                    ]
                })
                summary_df.to_excel(writer, sheet_name=table[:31], index=False, startrow=0)
                null_df.to_excel(writer, sheet_name=table[:31], index=False, startrow=10)

    output.seek(0)

    st.markdown("---")
    st.download_button(
        label="📅 Download Full Summary Report (Excel)",
        data=output,
        file_name=f"{selected_pg_db}_{selected_pg_schema}_vs_{selected_sf_db}_{selected_sf_schema}_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.markdown("---")

    # Proceed with comparison only if a valid table is selected
    if selected_table and selected_table != "None" and len(tables_postgresql) > 0:
        st.header(f"Comparison for Table: **{selected_table}**")

        row_count_source = data_fetcher.get_table_row_count(conn_postgresql, selected_table, source='postgresql',schema = selected_pg_schema)
        row_count_target = data_fetcher.get_table_row_count(conn_snowflake, selected_table, source='snowflake',schema = selected_sf_schema)
        match, count_source, count_target = comparator.compare_row_counts(row_count_source, row_count_target)

        st.subheader("Row Count Comparison")
        st.write(f"**Source (PostgreSQL):** {count_source} rows")
        st.write(f"**Target (Snowflake):** {count_target} rows")
        if match:
            st.success("Row counts match!")
        else:
            st.error("Row counts do NOT match!")

        df_counts = pd.DataFrame({"Source": [count_source], "Target": [count_target]}, index=["Row Count"])
        df_counts = df_counts.reset_index().melt(id_vars='index', value_vars=["Source", "Target"], var_name="Database", value_name="Rows")
        fig = px.bar(df_counts, x='Database', y='Rows', color='Database', title="Row Count Comparison")
        st.plotly_chart(fig)

        st.markdown("---")

        st.subheader("Column Count Comparison")
        schema_source = data_fetcher.get_table_schema(conn_postgresql, selected_table, source='postgresql',schema=selected_pg_schema)
        schema_target = data_fetcher.get_table_schema(conn_snowflake, selected_table, source='snowflake',schema=selected_sf_schema)
        st.write(f"**Source (PostgreSQL):** {schema_source.shape[0]} columns")
        st.write(f"**Target (Snowflake):** {schema_target.shape[0]} columns")
        if schema_source.shape[0] == schema_target.shape[0]:
            st.success("Column counts match!")
        else:
            st.error("Column counts do NOT match!")

        st.markdown("**Source Schema (PostgreSQL):**")
        st.dataframe(schema_source[['column_name', 'data_type']])
        st.markdown("**Target Schema (Snowflake):**")
        st.dataframe(schema_target[['COLUMN_NAME','DATA_TYPE']])

        st.markdown("---")

        st.subheader("Sample Data Comparison")
        sample_source = data_fetcher.get_sample_data(conn_postgresql, selected_table, n=120, source='postgresql',schema=selected_pg_schema)
        sample_target = data_fetcher.get_sample_data(conn_snowflake, selected_table, n=120, source='snowflake',schema=selected_sf_schema)

        st.markdown("**Source Sample Data (PostgreSQL):**")
        st.dataframe(sample_source)

        st.markdown("**Target Sample Data (Snowflake):**")
        st.dataframe(sample_target)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Duplicate Row Count (PostgreSQL):**")
            duplicates_sql = quality_checks.check_duplicates(sample_source)
            st.write(f'🔁 {duplicates_sql}')

        with col2:
            st.markdown("**Duplicate Row Count (Snowflake):**")
            duplicates_snowflake = quality_checks.check_duplicates(sample_target)
            st.write(f'🔁 {duplicates_snowflake}')

        st.markdown("---")
        # Data Quality Checks on source
        st.subheader("Data Quality Checks")

        # PostgreSQL nulls
        st.markdown("**Null Value Percentage per Column (PostgreSQL):**")
        nulls_sql = quality_checks.check_nulls(sample_source)
        nulls_df_sql = nulls_sql.reset_index()
        nulls_df_sql.columns = ['Column Name', 'Percentage (%)']
        nulls_df_sql['Column Name'] = nulls_df_sql['Column Name'].str.upper()  # Convert values to uppercase
        st.dataframe(nulls_df_sql, use_container_width=True)

        # Snowflake nulls
        st.markdown("**Null Value Percentage per Column (Snowflake):**")
        nulls_sf = quality_checks.check_nulls(sample_target)
        nulls_df_sf = nulls_sf.reset_index()
        nulls_df_sf.columns = ['Column Name', 'Percentage (%)']
        nulls_df_sf['Column Name'] = nulls_df_sf['Column Name'].str.upper()  # Convert values to uppercase
        st.dataframe(nulls_df_sf, use_container_width=True)

        st.markdown("---")
        st.subheader(f"📊 Summary Report - {selected_table}")

        summary_data = {
            "Check": [
                "Table Presence in Both DBs",
                "Row Count Match",
                "Column Count Match",
                "Duplicate Rows (PostgreSQL)",
                "Duplicate Rows (Snowflake)"
            ],
            "Result": [
                "✅ Present in both" if selected_table in common_tables else "❌ Missing in one",
                "✅ Match" if match else "❌ Mismatch",
                "✅ Match" if schema_source.shape[0] == schema_target.shape[0] else "❌ Mismatch",
                f"{duplicates_sql} duplicates",
                f"{duplicates_snowflake} duplicates"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("##### 🧪 Null Value Comparison (Source vs Target)")
        # Get null percentages and round to 0 decimals
        nulls_sqlserver = quality_checks.check_nulls(sample_source).round(0)
        nulls_snowflake = quality_checks.check_nulls(sample_target).round(0)

        # Standardize column names to uppercase
        nulls_sqlserver.index = nulls_sqlserver.index.str.upper()
        nulls_snowflake.index = nulls_snowflake.index.str.upper()

        # Combine and compare
        null_comparison = pd.concat([nulls_sqlserver, nulls_snowflake], axis=1)
        null_comparison.columns = ['PostgreSQL (%)', 'Snowflake (%)']

        # Replace NaN with 0 before calculating difference
        null_comparison.fillna(0, inplace=True)

        # Calculate and cast
        null_comparison['Difference'] = (null_comparison['PostgreSQL (%)'] - null_comparison['Snowflake (%)']).abs().astype(int)
        null_comparison[['PostgreSQL (%)', 'Snowflake (%)']] = null_comparison[['PostgreSQL (%)', 'Snowflake (%)']].astype(int)

        # Prepare for display
        null_comparison.reset_index(inplace=True)
        null_comparison.rename(columns={'index': 'Column Name'}, inplace=True)

        # Highlight differences
        def highlight_diff(val):
            return 'background-color: red' if val > 0 else ''

        # Display with highlighting
        st.dataframe(null_comparison.style.applymap(highlight_diff, subset=['Difference']), use_container_width=True)
    else:
        st.info("👆 Please select a table from the dropdown above to view comparison details.")


# Close connections
conn_postgresql.close()
if conn_snowflake:
    conn_snowflake.close()