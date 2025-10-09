import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Import our modules
# Note: Credentials are loaded in their respective config files
# - Source (PostgreSQL): config/postgresql_config.py loads from credentials/.env.source
# - Target (Snowflake): config/snowflake_config.py loads from credentials/.env.target
# - Target (Fabric): config/fabric_config.py loads from credentials/.env.fabric
from config.postgresql_config import get_postgresql_connection
from config.snowflake_config import get_snowflake_connection
from config.fabric_config import get_fabric_connection
from scripts import data_fetcher, comparator, quality_checks

# Title and description
st.title("Data Migration Assist")
st.markdown("This app compares table data between source and target databases during cloud migration.")

# Sidebar: Database and Schema Selection
with st.sidebar:
    st.image("Logo1.png", width=120)
    st.markdown("---")

    # Source Database Type Selection
    st.markdown("## 📊 Source Database")
    source_type = st.radio("Select Source Type", ["PostgreSQL", "Fabric"], key="source_type")

    # Initialize source variables
    conn_source = None
    source_db_list = []
    source_schemas = []
    tables_source = []
    selected_source_db = None
    selected_source_schema = None

    # Source Connection Section
    if source_type == "PostgreSQL":
        st.markdown("### 🔍 PostgreSQL Connection")

        # Fetch all PostgreSQL databases
        conn_master = get_postgresql_connection(database="postgres")
        source_db_list = data_fetcher.get_postgresql_databases(conn_master)
        conn_master.close()

        selected_source_db = st.selectbox("Select PostgreSQL Database", source_db_list, key="source_db")

        # Connect to selected PostgreSQL database
        conn_source = get_postgresql_connection(database=selected_source_db)

        # Fetch schemas for selected PostgreSQL database
        source_schemas = data_fetcher.get_postgresql_schemas(conn_source)
        selected_source_schema = st.selectbox("Select PostgreSQL Schema", source_schemas, key="source_schema")

        # Fetch tables for selected PostgreSQL schema
        tables_source = data_fetcher.get_table_list(conn_source, source='postgresql', schema=selected_source_schema)

    elif source_type == "Fabric":
        st.markdown("### 🏭 Fabric Connection")

        try:
            # Initial Fabric connection to fetch databases
            conn_fabric_temp = get_fabric_connection()
            source_db_list = data_fetcher.get_fabric_databases(conn_fabric_temp)
            conn_fabric_temp.close()

            selected_source_db = st.selectbox("Select Fabric Database", source_db_list, key="source_db")

            # Connect to selected Fabric database
            conn_source = get_fabric_connection(database=selected_source_db)

            # Fetch schemas for selected Fabric database
            source_schemas = data_fetcher.get_fabric_schemas(conn_source)
            selected_source_schema = st.selectbox("Select Fabric Schema", source_schemas, key="source_schema")

            # Fetch tables for selected Fabric schema
            tables_source = data_fetcher.get_table_list(conn_source, source='fabric', schema=selected_source_schema)

        except Exception as e:
            st.warning(f"Fabric connection error: {e}")
            selected_source_schema = None

    st.markdown("---")

    # Target Database Type Selection
    st.markdown("## 🎯 Target Database")
    target_type = st.radio("Select Target Type", ["Snowflake", "Fabric"], key="target_type")

    # Initialize target variables
    conn_target = None
    target_db_list = []
    target_schemas = []
    tables_target = []
    selected_target_db = None
    selected_target_schema = None

    # Target Connection Section
    if target_type == "Snowflake":
        st.markdown("### ❄️ Snowflake Connection")

        try:
            # Initial Snowflake connection to fetch databases
            conn_snowflake_temp = get_snowflake_connection()
            target_db_list = data_fetcher.get_snowflake_databases(conn_snowflake_temp)
            conn_snowflake_temp.close()

            selected_target_db = st.selectbox("Select Snowflake Database", target_db_list, key="target_db")

            # Connect to selected Snowflake database
            conn_target = get_snowflake_connection(database=selected_target_db)

            # Fetch schemas for selected Snowflake database
            target_schemas = data_fetcher.get_snowflake_schemas(conn_target)
            selected_target_schema = st.selectbox("Select Snowflake Schema", target_schemas, key="target_schema")

            # Fetch tables for selected Snowflake schema
            tables_target = data_fetcher.get_table_list(conn_target, source='snowflake', schema=selected_target_schema)

        except Exception as e:
            st.warning(f"Snowflake connection error: {e}")
            selected_target_schema = None

    elif target_type == "Fabric":
        st.markdown("### 🏭 Fabric Connection")

        try:
            # Initial Fabric connection to fetch databases
            conn_fabric_temp = get_fabric_connection()
            target_db_list = data_fetcher.get_fabric_databases(conn_fabric_temp)
            conn_fabric_temp.close()

            selected_target_db = st.selectbox("Select Fabric Database", target_db_list, key="target_db")

            # Connect to selected Fabric database
            conn_target = get_fabric_connection(database=selected_target_db)

            # Fetch schemas for selected Fabric database
            target_schemas = data_fetcher.get_fabric_schemas(conn_target)
            selected_target_schema = st.selectbox("Select Fabric Schema", target_schemas, key="target_schema")

            # Fetch tables for selected Fabric schema
            tables_target = data_fetcher.get_table_list(conn_target, source='fabric', schema=selected_target_schema)

        except Exception as e:
            st.warning(f"Fabric connection error: {e}")
            selected_target_schema = None

    st.markdown("---")

    # Table Selection (from source tables)
    st.markdown("## 📊 Table Selection")
    selected_table = st.selectbox("Select a Table to Compare", tables_source, key="table_select")

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
tables_source_upper = [t.upper() for t in tables_source]
tables_target_upper = [t.upper() for t in tables_target]

# Find common tables (case-insensitive)
common_tables_upper = list(set(tables_source_upper) & set(tables_target_upper))
common_tables = [t for t in tables_source if t.upper() in common_tables_upper]

# Find tables only in source (case-insensitive)
source_only_upper = list(set(tables_source_upper) - set(tables_target_upper))
source_only = [t for t in tables_source if t.upper() in source_only_upper]

# Find tables only in target (case-insensitive)
target_only_upper = list(set(tables_target_upper) - set(tables_source_upper))
target_only = [t for t in tables_target if t.upper() in target_only_upper]

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### ✅ Common Tables")
    st.write(common_tables)

with col2:
    st.markdown(f"#### ❌ Tables only in {source_type}")
    st.write(source_only)
    st.markdown(f"#### ❌ Tables only in {target_type}")
    st.write(target_only)

# Convert source and target type to lowercase for passing to data_fetcher functions
source_db_type = source_type.lower()
target_db_type = target_type.lower()

# --- Full Summary Section ---
if st.session_state.get("generate_summary", False):
    st.header("📄 Full Schema-Level Summary Report")
    output = BytesIO()
    with st.expander("Table's Summary"):
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for table in common_tables:
                row_source = data_fetcher.get_table_row_count(conn_source, table, source_db_type, selected_source_schema)
                row_target = data_fetcher.get_table_row_count(conn_target, table, target_db_type, selected_target_schema)
                match, count_source, count_target = comparator.compare_row_counts(row_source, row_target)

                schema_source = data_fetcher.get_table_schema(conn_source, table, source_db_type, selected_source_schema)
                schema_target = data_fetcher.get_table_schema(conn_target, table, target_db_type, selected_target_schema)
                column_match = schema_source.shape[0] == schema_target.shape[0]

                sample_source = data_fetcher.get_sample_data(conn_source, table, 120, source_db_type, selected_source_schema)
                sample_target = data_fetcher.get_sample_data(conn_target, table, 120, target_db_type, selected_target_schema)
                dup_source = quality_checks.check_duplicates(sample_source)
                dup_target = quality_checks.check_duplicates(sample_target)
                null_source = quality_checks.check_nulls(sample_source).round(0)
                null_target = quality_checks.check_nulls(sample_target).round(0)

                null_source.index = null_source.index.str.upper()
                null_target.index = null_target.index.str.upper()
                null_df = pd.concat([null_source, null_target], axis=1).fillna(0)
                null_df.columns = [f"{source_type} (%)", f"{target_type} (%)"]
                null_df["Difference"] = (null_df[f"{source_type} (%)"] - null_df[f"{target_type} (%)"]).abs().astype(int)
                null_df = null_df.astype(int).reset_index().rename(columns={"index": "Column Name"})

                ## View Data
                st.markdown("---")
                st.subheader(f"📊 Summary Report - {table}")

                sample_source = data_fetcher.get_sample_data(conn_source, table, n=120, source=source_db_type, schema=selected_source_schema)
                sample_target = data_fetcher.get_sample_data(conn_target, table, n=120, source=target_db_type, schema=selected_target_schema)
                duplicates_source = quality_checks.check_duplicates(sample_source)
                duplicates_target = quality_checks.check_duplicates(sample_target)

                summary_data = {
                    "Check": [
                        "Table Presence in Both DBs",
                        "Row Count Match",
                        "Column Count Match",
                        f"Duplicate Rows ({source_type})",
                        f"Duplicate Rows ({target_type})"
                    ],
                    "Result": [
                        "✅ Present in both" if table in common_tables else "❌ Missing in one",
                        "✅ Match" if match else "❌ Mismatch",
                        "✅ Match" if schema_source.shape[0] == schema_target.shape[0] else "❌ Mismatch",
                        f"{duplicates_source} duplicates",
                        f"{duplicates_target} duplicates"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)

                st.markdown("##### 🧪 Null Value Comparison (Source vs Target)")
                # Get null percentages and round to 0 decimals
                nulls_source = quality_checks.check_nulls(sample_source).round(0)
                nulls_target = quality_checks.check_nulls(sample_target).round(0)

                # Standardize column names to uppercase
                nulls_source.index = nulls_source.index.str.upper()
                nulls_target.index = nulls_target.index.str.upper()

                # Combine and compare
                null_comparison = pd.concat([nulls_source, nulls_target], axis=1)
                null_comparison.columns = [f'{source_type} (%)', f'{target_type} (%)']

                # Replace NaN with 0 before calculating difference
                null_comparison.fillna(0, inplace=True)

                # Calculate and cast
                null_comparison['Difference'] = (null_comparison[f'{source_type} (%)'] - null_comparison[f'{target_type} (%)']).abs().astype(int)
                null_comparison[[f'{source_type} (%)', f'{target_type} (%)']] = null_comparison[[f'{source_type} (%)', f'{target_type} (%)']].astype(int)

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
                        "Column Count Match", f"Duplicates {source_type}", f"Duplicates {target_type}"
                    ],
                    "Value": [
                        count_source, count_target, match, column_match, dup_source, dup_target
                    ]
                })
                summary_df.to_excel(writer, sheet_name=table[:31], index=False, startrow=0)
                null_df.to_excel(writer, sheet_name=table[:31], index=False, startrow=10)

    output.seek(0)

    st.markdown("---")
    st.download_button(
        label="📅 Download Full Summary Report (Excel)",
        data=output,
        file_name=f"{selected_source_db}_{selected_source_schema}_vs_{selected_target_db}_{selected_target_schema}_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.markdown("---")

    # Proceed with comparison only if a valid table is selected
    if selected_table and selected_table != "None" and len(tables_source) > 0:
        st.header(f"Comparison for Table: **{selected_table}**")

        row_count_source = data_fetcher.get_table_row_count(conn_source, selected_table, source=source_db_type, schema=selected_source_schema)
        row_count_target = data_fetcher.get_table_row_count(conn_target, selected_table, source=target_db_type, schema=selected_target_schema)
        match, count_source, count_target = comparator.compare_row_counts(row_count_source, row_count_target)

        st.subheader("Row Count Comparison")
        st.write(f"**Source ({source_type}):** {count_source} rows")
        st.write(f"**Target ({target_type}):** {count_target} rows")
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
        schema_source = data_fetcher.get_table_schema(conn_source, selected_table, source=source_db_type, schema=selected_source_schema)
        schema_target = data_fetcher.get_table_schema(conn_target, selected_table, source=target_db_type, schema=selected_target_schema)
        st.write(f"**Source ({source_type}):** {schema_source.shape[0]} columns")
        st.write(f"**Target ({target_type}):** {schema_target.shape[0]} columns")
        if schema_source.shape[0] == schema_target.shape[0]:
            st.success("Column counts match!")
        else:
            st.error("Column counts do NOT match!")

        st.markdown(f"**Source Schema ({source_type}):**")
        # Display appropriate column names based on source type
        if source_db_type == 'postgresql':
            st.dataframe(schema_source[['column_name', 'data_type']])
        else:
            st.dataframe(schema_source[['COLUMN_NAME','DATA_TYPE']])

        st.markdown(f"**Target Schema ({target_type}):**")
        if target_db_type == 'postgresql':
            st.dataframe(schema_target[['column_name', 'data_type']])
        else:
            st.dataframe(schema_target[['COLUMN_NAME','DATA_TYPE']])

        st.markdown("---")

        st.subheader("Sample Data Comparison")
        sample_source = data_fetcher.get_sample_data(conn_source, selected_table, n=120, source=source_db_type, schema=selected_source_schema)
        sample_target = data_fetcher.get_sample_data(conn_target, selected_table, n=120, source=target_db_type, schema=selected_target_schema)

        st.markdown(f"**Source Sample Data ({source_type}):**")
        st.dataframe(sample_source)

        st.markdown(f"**Target Sample Data ({target_type}):**")
        st.dataframe(sample_target)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Duplicate Row Count ({source_type}):**")
            duplicates_source = quality_checks.check_duplicates(sample_source)
            st.write(f'🔁 {duplicates_source}')

        with col2:
            st.markdown(f"**Duplicate Row Count ({target_type}):**")
            duplicates_target = quality_checks.check_duplicates(sample_target)
            st.write(f'🔁 {duplicates_target}')

        st.markdown("---")
        # Data Quality Checks on source
        st.subheader("Data Quality Checks")

        # Source nulls
        st.markdown(f"**Null Value Percentage per Column ({source_type}):**")
        nulls_source = quality_checks.check_nulls(sample_source)
        nulls_df_source = nulls_source.reset_index()
        nulls_df_source.columns = ['Column Name', 'Percentage (%)']
        nulls_df_source['Column Name'] = nulls_df_source['Column Name'].str.upper()
        st.dataframe(nulls_df_source, use_container_width=True)

        # Target nulls
        st.markdown(f"**Null Value Percentage per Column ({target_type}):**")
        nulls_target = quality_checks.check_nulls(sample_target)
        nulls_df_target = nulls_target.reset_index()
        nulls_df_target.columns = ['Column Name', 'Percentage (%)']
        nulls_df_target['Column Name'] = nulls_df_target['Column Name'].str.upper()
        st.dataframe(nulls_df_target, use_container_width=True)

        st.markdown("---")
        st.subheader(f"📊 Summary Report - {selected_table}")

        summary_data = {
            "Check": [
                "Table Presence in Both DBs",
                "Row Count Match",
                "Column Count Match",
                f"Duplicate Rows ({source_type})",
                f"Duplicate Rows ({target_type})"
            ],
            "Result": [
                "✅ Present in both" if selected_table in common_tables else "❌ Missing in one",
                "✅ Match" if match else "❌ Mismatch",
                "✅ Match" if schema_source.shape[0] == schema_target.shape[0] else "❌ Mismatch",
                f"{duplicates_source} duplicates",
                f"{duplicates_target} duplicates"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("##### 🧪 Null Value Comparison (Source vs Target)")
        # Get null percentages and round to 0 decimals
        nulls_source_cmp = quality_checks.check_nulls(sample_source).round(0)
        nulls_target_cmp = quality_checks.check_nulls(sample_target).round(0)

        # Standardize column names to uppercase
        nulls_source_cmp.index = nulls_source_cmp.index.str.upper()
        nulls_target_cmp.index = nulls_target_cmp.index.str.upper()

        # Combine and compare
        null_comparison = pd.concat([nulls_source_cmp, nulls_target_cmp], axis=1)
        null_comparison.columns = [f'{source_type} (%)', f'{target_type} (%)']

        # Replace NaN with 0 before calculating difference
        null_comparison.fillna(0, inplace=True)

        # Calculate and cast
        null_comparison['Difference'] = (null_comparison[f'{source_type} (%)'] - null_comparison[f'{target_type} (%)']).abs().astype(int)
        null_comparison[[f'{source_type} (%)', f'{target_type} (%)']] = null_comparison[[f'{source_type} (%)', f'{target_type} (%)']].astype(int)

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
if conn_source:
    conn_source.close()
if conn_target:
    conn_target.close()
