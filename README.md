# Financial Data Reconciliation & Exception Reporting Automation

A Python-based financial reconciliation tool that compares an internal ledger with a bank statement, identifies discrepancies, validates data quality, and generates an automated Excel exception report.

## Business Problem

Financial teams often compare ledger records against bank statements manually. This becomes time-consuming and error-prone when thousands of transactions are involved.

This project automates that reconciliation workflow and separates normal transactions from exceptions that require further review.

## What The Project Does

The system:

1. Generates 5,000 synthetic financial transactions.
2. Creates an internal ledger and bank statement dataset.
3. Matches records using transaction ID.
4. Identifies reconciliation exceptions.
5. Performs data-quality validation.
6. Applies review rules to prioritize important exceptions.
7. Generates reconciliation results as CSV.
8. Generates an Excel exception report for review.

## Reconciliation Checks

The engine identifies:

- Missing in Bank
- Missing in Ledger
- Duplicate Transactions
- Amount Mismatches
- Date Mismatches
- Missing Vendor Fields

## Data Quality Validation

The system also checks for:

- Invalid dates
- Invalid amounts
- Negative amounts
- Missing transaction IDs
- Duplicate transaction IDs
- Missing required columns

Edge-case testing was performed using intentionally invalid records to verify that invalid amounts, negative amounts, and missing transaction IDs are detected correctly.

## Matching Rules

The reconciliation engine uses:

- Transaction ID as the primary matching key
- ₹1 amount tolerance
- 2-day date tolerance

Records that do not meet the matching rules are classified as exceptions.

Exceptions are then evaluated using review rules based on factors such as transaction amount and discrepancy size.

## Results

The final end-to-end pipeline processes:

| Metric | Result |
|---|---:|
| Reconciliation Records | 5,000 |
| Matched Records | 4,550 |
| Auto-Match Rate | 91.00% |
| Reconciliation Findings | 450 |
| Exceptions Requiring Review | 63 |

## Exception Breakdown

| Exception Type | Count |
|---|---:|
| Missing in Bank | 100 |
| Missing in Ledger | 75 |
| Amount Mismatch | 100 |
| Date Mismatch | 75 |
| Missing Vendor Fields | 50 |
| Duplicate Transactions | 50 |

## Excel Report

The generated Excel workbook contains:

### Summary
Overall reconciliation metrics.

### Exception Breakdown
Counts of each reconciliation issue.

### Severity Breakdown
Distribution of exceptions requiring review.

### Exceptions Tracker
Transaction-level details including:

- Transaction ID
- Issue Type
- Ledger Date
- Bank Date
- Vendors
- Ledger Amount
- Bank Amount
- Amount Difference
- Date Difference
- Severity
- Review Reason

### Data Quality
Summary of detected data-quality issues.

## Technology Stack

- Python
- Pandas
- NumPy
- openpyxl
- Excel
- Git
- GitHub

## Project Structure

```text
financial-data-reconciliation/
│
├── data/
│   ├── bank_statement.csv
│   ├── internal_ledger.csv
│   └── reconciliation_results.csv
│
├── output/
│   └── reconciliation_report.xlsx
│
├── src/
│   ├── generate_data.py
│   ├── reconcile.py
│   └── generate_report.py
│
├── main.py
├── README.md
├── requirements.txt
└── .gitignore