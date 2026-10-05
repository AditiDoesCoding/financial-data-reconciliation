import pandas as pd
import numpy as np
import random


SEED = 42
NUM_TRANSACTIONS = 5000

MISSING_IN_BANK_COUNT = 100
MISSING_IN_LEDGER_COUNT = 75
AMOUNT_MISMATCH_COUNT = 100
DATE_MISMATCH_COUNT = 75
MISSING_VENDOR_COUNT = 50
DUPLICATE_COUNT = 50


random.seed(SEED)
np.random.seed(SEED)


def generate_base_transactions():
    dates = pd.date_range(
        start="2026-01-01",
        end="2026-06-30",
        periods=NUM_TRANSACTIONS
    )

    vendors = [
        "ABC Suppliers",
        "Global Traders",
        "Metro Services",
        "Prime Industries",
        "Shree Enterprises",
        "Tech Solutions",
        "National Distributors",
        "Apex Systems",
        "Sunrise Enterprises",
        "Reliance Services"
    ]

    account_codes = [
        "AP-001",
        "AP-002",
        "AP-003",
        "EXP-001",
        "EXP-002",
        "EXP-003"
    ]

    transactions = pd.DataFrame({
        "transaction_id": [
            f"TXN{i:06d}"
            for i in range(1, NUM_TRANSACTIONS + 1)
        ],
        "date": dates,
        "vendor": np.random.choice(
            vendors,
            NUM_TRANSACTIONS
        ),
        "amount": np.round(
            np.random.uniform(
                500,
                250000,
                NUM_TRANSACTIONS
            ),
            2
        ),
        "account_code": np.random.choice(
            account_codes,
            NUM_TRANSACTIONS
        )
    })

    return transactions


def generate_data():
    base = generate_base_transactions()

    all_ids = list(base["transaction_id"])

    random.shuffle(all_ids)

    missing_in_bank_ids = all_ids[
        :MISSING_IN_BANK_COUNT
    ]

    missing_in_ledger_ids = all_ids[
        MISSING_IN_BANK_COUNT:
        MISSING_IN_BANK_COUNT + MISSING_IN_LEDGER_COUNT
    ]

    remaining_ids = all_ids[
        MISSING_IN_BANK_COUNT + MISSING_IN_LEDGER_COUNT:
    ]

    amount_mismatch_ids = remaining_ids[
        :AMOUNT_MISMATCH_COUNT
    ]

    date_mismatch_ids = remaining_ids[
        AMOUNT_MISMATCH_COUNT:
        AMOUNT_MISMATCH_COUNT + DATE_MISMATCH_COUNT
    ]

    vendor_missing_ids = remaining_ids[
        AMOUNT_MISMATCH_COUNT + DATE_MISMATCH_COUNT:
        AMOUNT_MISMATCH_COUNT + DATE_MISMATCH_COUNT + MISSING_VENDOR_COUNT
    ]

    duplicate_ids = remaining_ids[
        AMOUNT_MISMATCH_COUNT + DATE_MISMATCH_COUNT + MISSING_VENDOR_COUNT:
        AMOUNT_MISMATCH_COUNT + DATE_MISMATCH_COUNT + MISSING_VENDOR_COUNT + DUPLICATE_COUNT
    ]

    # ---------------------------------------------------------
    # LEDGER
    # ---------------------------------------------------------

    ledger = base[
        ~base["transaction_id"].isin(
            missing_in_ledger_ids
        )
    ].copy()

    # ---------------------------------------------------------
    # BANK
    # ---------------------------------------------------------

    bank = base[
        ~base["transaction_id"].isin(
            missing_in_bank_ids
        )
    ].copy()

    # Bank does not contain account_code
    bank = bank[
        [
            "transaction_id",
            "date",
            "vendor",
            "amount"
        ]
    ].copy()

    # ---------------------------------------------------------
    # AMOUNT MISMATCHES
    # ---------------------------------------------------------

    for transaction_id in amount_mismatch_ids:

        index = bank.index[
            bank["transaction_id"] == transaction_id
        ]

        if len(index) > 0:
            idx = index[0]

            original_amount = bank.loc[
                idx,
                "amount"
            ]

            if random.random() < 0.5:
                bank.loc[
                    idx,
                    "amount"
                ] = round(
                    original_amount + random.choice(
                        [10, 25, 50, 100]
                    ),
                    2
                )
            else:
                bank.loc[
                    idx,
                    "amount"
                ] = round(
                    original_amount * random.uniform(
                        0.30,
                        0.80
                    ),
                    2
                )

    # ---------------------------------------------------------
    # DATE MISMATCHES
    # ---------------------------------------------------------

    for transaction_id in date_mismatch_ids:

        index = bank.index[
            bank["transaction_id"] == transaction_id
        ]

        if len(index) > 0:
            idx = index[0]

            bank.loc[
                idx,
                "date"
            ] = bank.loc[
                idx,
                "date"
            ] + pd.Timedelta(
                days=random.choice([3, 4, 5])
            )

    # ---------------------------------------------------------
    # MISSING VENDOR
    # ---------------------------------------------------------

    for transaction_id in vendor_missing_ids:

        index = bank.index[
            bank["transaction_id"] == transaction_id
        ]

        if len(index) > 0:
            idx = index[0]

            bank.loc[
                idx,
                "vendor"
            ] = np.nan

    # ---------------------------------------------------------
    # DUPLICATES
    # ---------------------------------------------------------

    duplicate_rows = bank[
        bank["transaction_id"].isin(
            duplicate_ids
        )
    ].copy()

    bank = pd.concat(
        [bank, duplicate_rows],
        ignore_index=True
    )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    ledger.to_csv(
        "data/internal_ledger.csv",
        index=False
    )

    bank.to_csv(
        "data/bank_statement.csv",
        index=False
    )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    unique_ids = set(
        ledger["transaction_id"]
    ).union(
        set(bank["transaction_id"])
    )

    duplicate_count = (
        bank["transaction_id"]
        .duplicated()
        .sum()
    )

    missing_in_bank_actual = len(
        set(ledger["transaction_id"])
        - set(bank["transaction_id"])
    )

    missing_in_ledger_actual = len(
        set(bank["transaction_id"])
        - set(ledger["transaction_id"])
    )

    print("=" * 65)
    print("FINANCIAL DATA RECONCILIATION")
    print("SYNTHETIC DATA GENERATION")
    print("=" * 65)

    print(f"Underlying transactions: {NUM_TRANSACTIONS}")
    print(f"Ledger records: {len(ledger)}")
    print(f"Bank records: {len(bank)}")
    print(f"Unique reconciliation IDs: {len(unique_ids)}")

    print("\nGENERATED EXCEPTIONS")
    print(
        f"Missing in bank: {missing_in_bank_actual}"
    )
    print(
        f"Missing in ledger: {missing_in_ledger_actual}"
    )
    print(
        f"Amount mismatches: {AMOUNT_MISMATCH_COUNT}"
    )
    print(
        f"Date mismatches: {DATE_MISMATCH_COUNT}"
    )
    print(
        f"Missing vendor fields: {MISSING_VENDOR_COUNT}"
    )
    print(
        f"Duplicate bank rows: {duplicate_count}"
    )

    print("\nFILES SAVED")
    print(
        "Ledger: data/internal_ledger.csv"
    )
    print(
        "Bank: data/bank_statement.csv"
    )

    print("=" * 65)


if __name__ == "__main__":
    generate_data()