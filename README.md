# Automated Data Engineering & QA Pipeline

## Description
**OptaLive** is a backend data engineering pipeline and automated Quality Assurance (QA) rules engine that models the operational workflow of an in-ground sports data correspondent. Built using StatsBomb Open Data (English Premier League 2015/2016 season), the system ingests raw JSON feeds, validates pre-match team sheets, processes chronological match incidents, and computes a quantitative Match Health Score to guarantee broadcast-grade data integrity.

---

## The Problem
In-ground sports event collection is high-pressure and manual, making it prone to critical data anomalies:
* **Incomplete Team Sheets:** Matches starting without confirmed squad sizes, missing jersey numbers, or unverified starting XIs.
* **Timestamp & Sequence Errors:** Out-of-order match events, invalid period assignments, or missing timestamps.
* **Attribution Discrepancies:** Goals or disciplinary actions linked incorrectly to missing player or team IDs.
* **Disciplinary Inconsistencies:** Unflagged secondary yellow cards leading to unrecorded red card ejections.

---

## The Solution
OptaLive solves these challenges through a modular, automated ETL and validation pipeline:
1. **Ingested Extraction (`data_loader.py`):** Efficiently parses nested raw JSON match files, lineups, and event streams.
2. **Preprocessing (`preprocessing.py`):** Standardizes team rosters, verifies squad readiness thresholds, and filters chronological key events (Goals, Bookings, Substitutions).
3. **Automated QA Rules Engine (`validation.py`):** Scans the event stream against strict domain validation rules, classifying records into `Valid`, `Warning`, or `Error` statuses and computing an overall Match Health Score.

---

## Reporting & Notebook Workflow
The analysis and validation workflows are fully documented and executed via reproducible Jupyter notebooks:
* `01_data_ingestion.ipynb`: Raw JSON data parsing and exploration.
* `02_preprocessing.ipynb`: Team sheet verification and key event extraction.
* `03_validation_rules.ipynb`: Unit-testing individual QA rules and edge cases.
* `04_data_report.ipynb`: Executive summary generation and CSV audit report export (`reports/`).

---

## Tech Stack
* **Language:** Python 3.x
* **Data Processing & Analysis:** Pandas, NumPy
* **Data Storage:** JSON, CSV (`data/raw/`, `reports/`)
* **Environment:** Jupyter Notebooks (`notebooks/`)
* **Architecture:** Modular Python Scripts (`src/`)

---

## Project Structure
```text
optalive-pipeline/
│
├── data/
│   └── raw/ # Raw StatsBomb Open Data JSONs
    └── processed/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_validation_rules.ipynb
│   └── 04_data_report.ipynb   
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py     # Ingestion & parsing module
│   ├── preprocessing.py   # Roster & key event extraction module
│   └── validation.py      # Automated QA rules engine & health scoring
│
├── reports/               # Exported CSV audit logs & health reports
└── README.md
