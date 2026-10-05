import pandas as pd


LEDGER_PATH = "data/internal_ledger.csv"
BANK_PATH = "data/bank_statement.csv"
OUTPUT_PATH = "data/reconciliation_results.csv"

AMOUNT_TOLERANCE = 1.00
DATE_TOLERANCE_DAYS = 2


def load_data():
    ledger = pd.read_csv(
        LEDGER_PATH,
        parse_dates=["date"]
    )

    bank = pd.read_csv(
        BANK_PATH,
        parse_dates=["date"]
    )

    # Data-quality validation
    for name, df in [("Ledger", ledger), ("Bank", bank)]:
        required_columns = [
            "transaction_id",
            "date",
            "vendor",
            "amount"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"{name} is missing required columns: "
                f"{missing_columns}"
            )

        invalid_dates = df["date"].isna().sum()

        numeric_amounts = pd.to_numeric(
            df["amount"],
            errors="coerce"
        )

        invalid_amounts = numeric_amounts.isna().sum()
        negative_amounts = (numeric_amounts < 0).sum()
        missing_transaction_ids = df["transaction_id"].isna().sum()

        duplicate_transaction_ids = (
            df["transaction_id"]
            .duplicated(keep=False)
            .sum()
        )

        print(f"\n{name} DATA QUALITY CHECK")
        print(f"Invalid dates: {invalid_dates}")
        print(f"Invalid amounts: {invalid_amounts}")
        print(f"Negative amounts: {negative_amounts}")
        print(
            f"Missing transaction IDs: "
            f"{missing_transaction_ids}"
        )
        print(
            f"Duplicate transaction ID rows: "
            f"{duplicate_transaction_ids}"
        )

    return ledger, bank


def reconcile_transactions(ledger, bank):

    bank_duplicate_ids = (
        bank[
            bank.duplicated(
                "transaction_id",
                keep=False
            )
        ]["transaction_id"]
        .unique()
    )

    ledger_ids = set(
        ledger["transaction_id"]
    )

    bank_ids = set(
        bank["transaction_id"]
    )

    all_ids = sorted(
        ledger_ids.union(bank_ids)
    )

    results = []

    for transaction_id in all_ids:

        ledger_rows = ledger[
            ledger["transaction_id"] == transaction_id
        ]

        bank_rows = bank[
            bank["transaction_id"] == transaction_id
        ]

        ledger_exists = not ledger_rows.empty
        bank_exists = not bank_rows.empty

        status = "Matched"

        ledger_date = None
        bank_date = None

        ledger_vendor = None
        bank_vendor = None

        ledger_amount = None
        bank_amount = None

        amount_difference = None
        date_difference_days = None

        # Get ledger information
        if ledger_exists:
            ledger_row = ledger_rows.iloc[0]

            ledger_date = ledger_row["date"]
            ledger_vendor = ledger_row["vendor"]
            ledger_amount = ledger_row["amount"]

        # Get bank information
        if bank_exists:
            bank_row = bank_rows.iloc[0]

            bank_date = bank_row["date"]
            bank_vendor = bank_row["vendor"]
            bank_amount = bank_row["amount"]

        # Classification
        if not bank_exists:

            status = "Missing in Bank"

        elif not ledger_exists:

            status = "Missing in Ledger"

        elif transaction_id in bank_duplicate_ids:

            status = "Duplicate"

        else:

            amount_difference = abs(
                float(ledger_amount)
                - float(bank_amount)
            )

            date_difference_days = abs(
                (ledger_date - bank_date).days
            )

            # Amount tolerance
            if amount_difference > AMOUNT_TOLERANCE:

                status = "Amount Mismatch"

            # Date tolerance
            elif date_difference_days > DATE_TOLERANCE_DAYS:

                status = "Date Mismatch"

            # Missing vendor
            elif (
                pd.isna(bank_vendor)
                or str(bank_vendor).strip() == ""
            ):

                status = "Missing Vendor Field"

        results.append(
            {
                "transaction_id": transaction_id,
                "status": status,

                "ledger_date": ledger_date,
                "bank_date": bank_date,

                "ledger_vendor": ledger_vendor,
                "bank_vendor": bank_vendor,

                "ledger_amount": ledger_amount,
                "bank_amount": bank_amount,

                "amount_difference": amount_difference,
                "date_difference_days": date_difference_days,
            }
        )

    return pd.DataFrame(results)


def apply_review_rules(results):
    """
    Apply business materiality and control rules to determine
    which reconciliation findings require manual review.
    """

    results["review_required"] = "No"

    results["severity"] = "Low"

    results["review_reason"] = (
        "Auto-cleared by business rule"
    )

    # 1. Missing transactions
    material_missing = (
        results["status"].isin(
            [
                "Missing in Bank",
                "Missing in Ledger"
            ]
        )
        &
        (
            results["ledger_amount"]
            .fillna(results["bank_amount"])
            >= 200000
        )
    )

    results.loc[
        material_missing,
        "review_required"
    ] = "Yes"

    results.loc[
        material_missing,
        "severity"
    ] = "High"

    results.loc[
        material_missing,
        "review_reason"
    ] = "Material missing transaction"

    # 2. Amount mismatches
    material_amount_mismatch = (
        (results["status"] == "Amount Mismatch")
        &
        (
            results["amount_difference"]
            .fillna(0)
            >= 100000
        )
    )

    results.loc[
        material_amount_mismatch,
        "review_required"
    ] = "Yes"

    results.loc[
        material_amount_mismatch,
        "severity"
    ] = "High"

    results.loc[
        material_amount_mismatch,
        "review_reason"
    ] = "Material amount discrepancy"

    # 3. Date mismatches
    material_date_mismatch = (
        (results["status"] == "Date Mismatch")
        &
        (
            results["date_difference_days"]
            .fillna(0)
            >= 6
        )
    )

    results.loc[
        material_date_mismatch,
        "review_required"
    ] = "Yes"

    results.loc[
        material_date_mismatch,
        "severity"
    ] = "Medium"

    results.loc[
        material_date_mismatch,
        "review_reason"
    ] = "Significant date discrepancy"

    # 4. Duplicate transactions
    material_duplicate = (
        (results["status"] == "Duplicate")
        &
        (
            results["bank_amount"]
            .fillna(0)
            >= 200000
        )
    )

    results.loc[
        material_duplicate,
        "review_required"
    ] = "Yes"

    results.loc[
        material_duplicate,
        "severity"
    ] = "High"

    results.loc[
        material_duplicate,
        "review_reason"
    ] = "Material duplicate transaction"

    # 5. Missing vendor information
    material_missing_vendor = (
        (results["status"] == "Missing Vendor Field")
        &
        (
            results["ledger_amount"]
            .fillna(0)
            >= 200000
        )
    )

    results.loc[
        material_missing_vendor,
        "review_required"
    ] = "Yes"

    results.loc[
        material_missing_vendor,
        "severity"
    ] = "Medium"

    results.loc[
        material_missing_vendor,
        "review_reason"
    ] = (
        "Material transaction with missing vendor"
    )

    return results


def print_results(results):

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

    print("=" * 65)
    print("RECONCILIATION RESULTS")
    print("=" * 65)

    print(
        f"Total reconciliation records: "
        f"{total_records}"
    )

    print(
        f"Matched records: "
        f"{matched_records}"
    )

    print(
        f"Exception records: "
        f"{exception_records}"
    )

    print(
        f"Exceptions requiring review: "
        f"{review_records}"
    )

    print(
        f"Match rate: "
        f"{match_rate:.10f}%"
    )

    print("\nEXCEPTION BREAKDOWN")

    breakdown = (
        results["status"]
        .value_counts()
        .sort_index()
    )

    for status, count in breakdown.items():

        print(
            f"{status}: {count}"
        )

    print("\nREVIEW BREAKDOWN")

    review_breakdown = (
        results[
            results["review_required"] == "Yes"
        ]["severity"]
        .value_counts()
        .sort_index()
    )

    for severity, count in review_breakdown.items():

        print(
            f"{severity}: {count}"
        )


def main():

    ledger, bank = load_data()

    results = reconcile_transactions(
        ledger,
        bank
    )

    results = apply_review_rules(
        results
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print_results(
        results
    )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_PATH}"
    )

    print("=" * 65)


if __name__ == "__main__":
    main()