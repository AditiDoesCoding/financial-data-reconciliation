# Financial Data Reconciliation & Exception Reporting Automation

## What is this project?

This project automatically compares a company's internal ledger with its bank statement.

Instead of checking thousands of transactions manually, the Python program checks them automatically and identifies transactions that do not match.

## What does it do?

The project:

1. Generates 5,000 synthetic transactions.
2. Creates a ledger and bank statement.
3. Compares both using transaction ID.
4. Finds mismatches and data issues.
5. Identifies which issues need manual review.
6. Creates an Excel report.

## Results

- Total transactions: 5,000
- Automatically matched: 4,550
- Auto-match rate: 91%
- Reconciliation findings: 450
- Exceptions requiring review: 63

## Issues detected

The system checks for:

- Missing in Bank
- Missing in Ledger
- Duplicate transactions
- Amount mismatches
- Date mismatches
- Missing vendor information

## Tools Used

- Python
- Pandas
- NumPy
- openpyxl
- Excel

## How to Run

Install the required packages:

```bash
pip install -r requirements.txt