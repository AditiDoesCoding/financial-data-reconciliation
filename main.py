from src.generate_data import generate_data
from src.reconcile import (
    load_data,
    reconcile_transactions,
    apply_review_rules
)
from src.generate_report import generate_report


def main():

    print("\n")
    print("=" * 70)
    print("FINANCIAL DATA RECONCILIATION")
    print("END-TO-END AUTOMATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # STEP 1: Generate synthetic transaction data
    # ---------------------------------------------------------

    print("\n[1/3] Generating synthetic transaction data...\n")

    generate_data()

    # ---------------------------------------------------------
    # STEP 2: Reconcile ledger and bank statement
    # ---------------------------------------------------------

    print("\n[2/3] Running reconciliation engine...\n")

    ledger, bank = load_data()

    results = reconcile_transactions(
        ledger,
        bank
    )

    results = apply_review_rules(
        results
    )

    results.to_csv(
        "data/reconciliation_results.csv",
        index=False
    )

    # ---------------------------------------------------------
    # STEP 3: Generate Excel report
    # ---------------------------------------------------------

    print("\n[3/3] Generating Excel exception report...\n")

    generate_report()

    # ---------------------------------------------------------
    # FINAL RESULTS
    # ---------------------------------------------------------

    total_records = len(results)

    matched_records = (
        results["status"] == "Matched"
    ).sum()

    exception_records = (
        results["status"] != "Matched"
    ).sum()

    review_records = (
        results["review_required"] == "Yes"
    ).sum()

    match_rate = (
        matched_records
        / total_records
    ) * 100

    print("\n")
    print("=" * 70)
    print("FINAL RECONCILIATION SUMMARY")
    print("=" * 70)

    print(
        f"Total records:                 {total_records}"
    )

    print(
        f"Auto-matched records:          {matched_records}"
    )

    print(
        f"Auto-match rate:               {match_rate:.2f}%"
    )

    print(
        f"Reconciliation findings:       {exception_records}"
    )

    print(
        f"Exceptions requiring review:   {review_records}"
    )

    print("\n")
    print("OUTPUT FILES")
    print("-" * 70)

    print(
        "data/internal_ledger.csv"
    )

    print(
        "data/bank_statement.csv"
    )

    print(
        "data/reconciliation_results.csv"
    )

    print(
        "output/reconciliation_report.xlsx"
    )

    print("=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()