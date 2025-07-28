# Automated Daily Financial Reconciliation System

## Problem Statement
Manual reconciliation of financial transactions between internal sales records and payment processor reports is error-prone and time-consuming. This system automates daily reconciliation, detects discrepancies, and generates comprehensive reports.

## Features
- Synthetic data generation for testing reconciliation logic
- Automated loading and cleaning of sales and payment processor data
- Merging and comparison of records to identify:
  - Missing transactions
  - Amount mismatches
  - Failed payments
- Excel report generation with separate sheets for each discrepancy type
- Configurable paths and report settings

## Tech Stack
- Python 3.x
- pandas
- sqlite_utils
- openpyxl

## Setup & Installation
1. Clone the repository.
2. (Optional) Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Unix/macOS:
   source venv/bin/activate
   # On Windows (Command Prompt):
   venv\Scripts\activate
   # On Windows (Git Bash):
   source venv/Scripts/activate
   ```
3. Install dependencies:
   ```
   pip install pandas sqlite-utils openpyxl
   ```
4. Configure paths in `config.ini` if needed.

## Usage
1. Run [`src/setup_database.py`](src/setup_database.py:1) to generate synthetic sales data and payment processor reports:
   ```
   python src/setup_database.py
   ```
2. Run [`src/main.py`](src/main.py:1) to perform reconciliation and generate the Excel report:
   ```
   python src/main.py
   ```
3. Find the reconciliation report in the `/data/` directory.
 
- Uses open-source libraries: pandas, sqlite-utils, openpyxl.
