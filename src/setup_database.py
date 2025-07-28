"""
setup_database.py

Generates synthetic sales data and payment processor reports for automated daily financial reconciliation.
Creates a SQLite database and a CSV file with realistic discrepancies for testing reconciliation logic.
"""

import os
import random
import csv
from datetime import datetime, timedelta
import sqlite_utils

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "internal_sales.db")
CSV_PATH = os.path.join(DATA_DIR, "payment_processor_report.csv")

# Generate 100 synthetic sales records for the database
products = [f"P{str(i).zfill(3)}" for i in range(1, 21)]
base_date = datetime.now() - timedelta(days=120)
sales_rows = []
for i in range(1, 101):
    sale_date = (base_date + timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d")
    product_id = random.choice(products)
    amount = round(random.uniform(100, 1000), 2)
    sales_rows.append({
        "transaction_id": f"T{str(i).zfill(5)}",
        "sale_date": sale_date,
        "product_id": product_id,
        "amount": amount
    })

# Create SQLite DB and sales table
db = sqlite_utils.Database(DB_PATH)
db["sales"].insert_all(sales_rows, pk="transaction_id")

# Generate synthetic payment processor records with intentional discrepancies
csv_rows = []
matched_indices = random.sample(range(100), 96)
unmatched_indices = list(set(range(100)) - set(matched_indices))
amount_mismatch_indices = random.sample(matched_indices, 2)
missing_indices = random.sample(matched_indices, 2)

for idx in matched_indices:
    sale = sales_rows[idx]
    payment_gateway_id = sale["transaction_id"]
    transaction_date = sale["sale_date"]
    status = "completed"
    charged_amount = sale["amount"]
    # Introduce amount mismatch for selected records
    if idx in amount_mismatch_indices:
        charged_amount = round(charged_amount + random.uniform(-5, 5), 2)
    # Skip selected records to simulate missing payments
    if idx in missing_indices:
        continue
    csv_rows.append([
        payment_gateway_id,
        transaction_date,
        status,
        charged_amount
    ])

# Add one failed transaction (randomly pick from unmatched sales)
failed_idx = random.choice(unmatched_indices)
sale = sales_rows[failed_idx]
csv_rows.append([
    sale["transaction_id"],
    sale["sale_date"],
    "failed",
    sale["amount"]
])

# Add 2 records that are present in the CSV but missing from the database
for i in range(2):
    fake_id = f"X{str(i+1).zfill(5)}"
    fake_date = (base_date + timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d")
    fake_amount = round(random.uniform(100, 1000), 2)
    csv_rows.append([
        fake_id,
        fake_date,
        "completed",
        fake_amount
    ])

# Write the payment processor report to CSV
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["payment_gateway_id", "transaction_date", "status", "charged_amount"])
    writer.writerows(csv_rows)