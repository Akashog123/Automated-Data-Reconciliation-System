"""
main.py

Automated Daily Financial Reconciliation System.
Loads sales and payment processor data, cleans and merges records, identifies discrepancies, and generates reconciliation reports.
"""

import pandas as pd
import sqlite3
from typing import Tuple
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')
db_path = config.get('paths', 'db_path', fallback='data/internal_sales.db')
csv_path = config.get('paths', 'csv_path', fallback='data/payment_processor_report.csv')
report_dir = config.get('paths', 'report_dir', fallback='data')
report_prefix = config.get('report', 'report_prefix', fallback='reconciliation_report_')

def load_database_data(db_path: str, table_name: str) -> pd.DataFrame:
    """Load data from SQLite database table into a pandas DataFrame.

    Args:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to load.

    Returns:
        pd.DataFrame: DataFrame containing table data.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def load_csv_data(csv_path: str) -> pd.DataFrame:
    """Load data from CSV file into a pandas DataFrame.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing CSV data.
    """
    df = pd.read_csv(csv_path)
    return df

def clean_and_transform(df: pd.DataFrame, column_map: dict, date_columns: list) -> pd.DataFrame:
    """
    Standardize column names and date formats.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_map (dict): Mapping from old to new column names.
        date_columns (list): List of columns to parse as dates.

    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    # Strip and lowercase column names
    df.columns = df.columns.str.strip().str.lower()
    # Rename columns
    df = df.rename(columns=column_map)
    # Standardize date columns
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def merge_dataframes(db_df: pd.DataFrame, csv_df: pd.DataFrame, on: str) -> pd.DataFrame:
    """Merge two DataFrames with an outer join on the transaction ID.

    Args:
        db_df (pd.DataFrame): Database DataFrame.
        csv_df (pd.DataFrame): CSV DataFrame.
        on (str): Column name to join on.

    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    merged = pd.merge(db_df, csv_df, how='outer', on=on, suffixes=('_db', '_csv'), indicator=True)
    return merged

def identify_discrepancies(merged_df: pd.DataFrame, amount_col_db: str, amount_col_csv: str, status_col_db: str) -> dict:
    """
    Identify discrepancies between sales and payment processor data.

    Args:
        merged_df (pd.DataFrame): Merged DataFrame.
        amount_col_db (str): Amount column name from DB.
        amount_col_csv (str): Amount column name from CSV.
        status_col_db (str): Status column name from DB.

    Returns:
        dict: Dictionary of DataFrames for each discrepancy type.
    """
    missing_in_processor = merged_df[merged_df['_merge'] == 'left_only']
    missing_in_db = merged_df[merged_df['_merge'] == 'right_only']
    amount_mismatches = merged_df[
        (merged_df['_merge'] == 'both') &
        (merged_df[amount_col_db] != merged_df[amount_col_csv])
    ]
    failed_payments = merged_df[
        (merged_df.get(status_col_db) == 'failed') |
        (merged_df.get(f"{status_col_db}_db") == 'failed')
    ]
    return {
        'missing_in_processor': missing_in_processor,
        'missing_in_db': missing_in_db,
        'amount_mismatches': amount_mismatches,
        'failed_payments': failed_payments
    }

# --- Logging Setup ---
import logging
import os
from datetime import datetime
from openpyxl import Workbook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("reconciliation.log"),
        logging.StreamHandler()
    ]
)

def generate_excel_report(discrepancies: dict, report_dir: str, report_prefix: str):
    """Generate a timestamped Excel report with separate sheets for each discrepancy type.

    Args:
        discrepancies (dict): Dictionary of DataFrames for each discrepancy.
        report_dir (str): Directory to save the report.
        report_prefix (str): Prefix for the report filename.

    Returns:
        None
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{report_prefix}{timestamp}.xlsx"
    filepath = os.path.join(report_dir, filename)
    wb = Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)
    for sheet_name, df in discrepancies.items():
        ws = wb.create_sheet(title=sheet_name)
        # Write header
        ws.append(list(df.columns))
        # Write data rows
        for row in df.itertuples(index=False):
            ws.append(list(row))
    wb.save(filepath)
    logging.info(f"Excel report generated: {filepath}")

if __name__ == "__main__":
    try:
        logging.info("Starting daily financial reconciliation workflow.")
        # Example config values for demonstration
        db_table = config.get('paths', 'db_table', fallback='sales')
        column_map = {
            # Example mapping, adjust as needed
            'transaction_id': 'transaction_id',
            'amount': 'amount',
            'status': 'status',
            'date': 'date'
        }
        date_columns = ['date']
        merge_key = 'transaction_id'
        amount_col_db = 'amount_db'
        amount_col_csv = 'amount_csv'
        status_col_db = 'status_db'

        # Load data
        logging.info("Loading database data.")
        db_df = load_database_data(db_path, db_table)
        logging.info("Loading CSV data.")
        csv_df = load_csv_data(csv_path)

        # Clean and transform
        logging.info("Cleaning and transforming database data.")
        db_df = clean_and_transform(db_df, column_map, date_columns)
        logging.info("Cleaning and transforming CSV data.")
        csv_df = clean_and_transform(csv_df, column_map, date_columns)

        # Merge
        logging.info("Merging dataframes.")
        merged_df = merge_dataframes(db_df, csv_df, merge_key)

        # Identify discrepancies
        logging.info("Identifying discrepancies.")
        discrepancies = identify_discrepancies(merged_df, amount_col_db, amount_col_csv, status_col_db)

        # Generate Excel report
        generate_excel_report(discrepancies, report_dir, report_prefix)

        logging.info("Reconciliation workflow completed successfully.")

    except Exception as e:
        logging.error(f"Error during reconciliation workflow: {e}", exc_info=True)