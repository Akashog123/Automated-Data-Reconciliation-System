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
- Robust logging for audit and debugging
- Automated email alerts for discrepancies using Celery and Redis
- Linux deployment support
- Complete dependency management via requirements.txt

## Tech Stack
- Python 3.x
- pandas
- sqlite_utils
- openpyxl
- celery
- redis-py

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
3. Install all dependencies:
   ```
   pip install -r requirements.txt
   ```
4. **Install and start Redis server:**
   - On Linux (recommended for deployment):
     ```
     sudo apt-get install redis-server
     sudo service redis-server start
     ```
   - Or with Docker:
     ```
     docker run -d -p 6379:6379 redis
     ```
5. **Configure Celery worker:**
   - Example Celery configuration for Redis broker:
     ```python
     app.conf.broker_url = 'redis://localhost:6379/0'
     app.conf.result_backend = 'redis://localhost:6379/0'
     ```
   - Start the Celery worker:
     ```
     celery -A src.alerts worker -l INFO
     ```
   - For periodic tasks (automation):
     ```
     celery -A src.alerts worker -B -l INFO
     ```
6. **Configure email alerts:**
   - Set SMTP and email settings in `config.ini` as required for your environment.
   - Celery tasks will use these settings to send alert emails on reconciliation failures or discrepancies.

7. **Linux deployment notes:**
   - All scripts and services are compatible with Linux.
   - Use systemd or supervisor to manage long-running Celery workers and Redis server for production deployments.

## Logging

- The system uses Python's built-in logging module for detailed audit trails and error tracking.
- Logs are written to both console and log files for easy monitoring and debugging.
- Logging configuration can be customized in `config.ini`.

## Alerting & Automation

- **Celery** is used for asynchronous task processing and scheduling.
- **Redis** acts as the broker and result backend for Celery.
- Automated email alerts are triggered for reconciliation failures, missing transactions, or other critical events.
- Periodic tasks can be scheduled using Celery Beat (embedded with worker using `-B` flag).

## Usage

1. Run [`src/setup_database.py`](src/setup_database.py:1) to generate synthetic sales data and payment processor reports:
   ```
   python src/setup_database.py
   ```
2. Run [`src/main.py`](src/main.py:1) to perform reconciliation and generate the Excel report:
   ```
   python src/main.py
   ```
3. Celery worker will automatically send email alerts for detected discrepancies.
4. Find the reconciliation report in the `/data/` directory.

## Dependencies

- All required packages are listed in [`requirements.txt`](requirements.txt:1).
- Key dependencies:
  - pandas
  - sqlite-utils
  - openpyxl
  - celery
  - redis
  - any SMTP/email library required for alerts

## Linux Deployment

- All scripts and services are tested on Linux.
- Use systemd or supervisor for managing Redis and Celery worker processes.
- Example systemd service for Celery worker:
  ```
  [Unit]
  Description=Celery Worker Service
  After=network.target

  [Service]
  Type=simple
  User=youruser
  WorkingDirectory=/path/to/project
  ExecStart=/path/to/venv/bin/celery -A src.alerts worker -l INFO
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

## License

- Uses open-source libraries: pandas, sqlite-utils, openpyxl, celery, redis-py.
