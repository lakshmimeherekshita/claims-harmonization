import pandas as pd

from src.stage_tracker import StageTracker


# =========================================================
# Configuration
# =========================================================

FILE_PATH = "data/raw/source_b_claims.csv.xlsx"

START_DATE = pd.Timestamp("2018-01-01")
END_DATE = pd.Timestamp("2025-02-28")

TARGET_COLUMNS = [
    "SRC",
    "PATIENT_ID",
    "BIRTH_YEAR",
    "GENDER",
    "ZIP3",
    "CLAIM_ID",
    "SERVICE_DATE",
    "DIAGNOSIS_CODE",
    "PLACE_OF_SERVICE",
    "RENDERING_NPI",
    "REFERRING_NPI",
    "BILLING_NPI",
    "PRIMARY_PLAN_ID",
    "BILLED_AMOUNT",
]


# =========================================================
# Stage 1: Load Source B
# =========================================================

def load_source_b():
    """Load the raw Source B dataset."""

    return pd.read_excel(FILE_PATH)


# =========================================================
# Stage 2: Filter service dates
# =========================================================

def filter_service_dates(df, tracker=None):
    """
    Keep only records with service dates between
    2018-01-01 and 2025-02-28 inclusive.
    """

    df = df.copy()

    rows_in = len(df)

    df["svc_date"] = pd.to_datetime(
        df["svc_date"],
        errors="raise"
    )

    result = df[
        (df["svc_date"] >= START_DATE)
        & (df["svc_date"] <= END_DATE)
    ].copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    if tracker is not None:
        tracker.record(
            stage="Source B - Service date filter",
            rows_in=rows_in,
            rows_out=rows_out,
            reason="Dropped rows outside 2018-01-01 to 2025-02-28"
        )

    print("\n[Service date filter]")
    print("Rows in:", rows_in)
    print("Rows out:", rows_out)
    print("Rows dropped:", rows_dropped)
    print(
        "Allowed range:",
        START_DATE.date(),
        "to",
        END_DATE.date()
    )

    return result


# =========================================================
# Stage 3: Normalize diagnosis codes
# =========================================================

def normalize_diagnosis_codes(df, tracker=None):
    """
    Normalize diagnosis codes:
    - uppercase
    - remove dots
    - remove leading/trailing whitespace
    """

    df = df.copy()

    df["dx_code"] = (
        df["dx_code"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "", regex=False)
    )

    if tracker is not None:
        tracker.record(
            stage="Source B - Diagnosis normalization",
            rows_in=len(df),
            rows_out=len(df),
            reason=(
                "Normalized diagnosis codes to uppercase "
                "and removed dots/whitespace"
            )
        )

    return df


# =========================================================
# Stage 4: Enforce Source B grain
# =========================================================

def enforce_source_b_grain(df, tracker=None):
    """
    Source B target grain:

        CLAIM_ID + DIAGNOSIS_CODE

    Source B investigation showed no duplicate
    encounter_id + dx_code combinations.

    This function therefore validates the grain rather
    than silently removing records.
    """

    duplicate_mask = df.duplicated(
        subset=[
            "encounter_id",
            "dx_code"
        ],
        keep=False
    )

    duplicate_rows = df[duplicate_mask]

    print("\n[Source B grain validation]")
    print(
        "Rows at current diagnosis level:",
        len(df)
    )
    print(
        "Rows involved in duplicate encounter + diagnosis:",
        len(duplicate_rows)
    )

    if len(duplicate_rows) > 0:
        raise ValueError(
            "Source B contains duplicate "
            "encounter_id + dx_code combinations."
        )

    print("Grain validation passed.")
    print("Grain: encounter_id + dx_code")

    if tracker is not None:
        tracker.record(
            stage="Source B - Grain validation",
            rows_in=len(df),
            rows_out=len(df),
            reason=(
                "Validated CLAIM_ID + DIAGNOSIS_CODE grain; "
                "no duplicates found"
            )
        )

    return df.copy()


# =========================================================
# Stage 5: Map gender
# =========================================================

def map_gender(df):
    """
    Source B gender mapping.

    Assumption based on the observed source values:
        1 -> M
        2 -> F

    Source documentation did not explicitly provide
    this mapping, so the assumption is kept explicit.
    """

    df = df.copy()

    gender_mapping = {
        1: "M",
        2: "F"
    }

    df["GENDER"] = df["gender"].map(
        gender_mapping
    )

    if df["GENDER"].isna().any():

        invalid_values = (
            df.loc[
                df["GENDER"].isna(),
                "gender"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            f"Unexpected gender values found: {invalid_values}"
        )

    return df


# =========================================================
# Stage 6: Map Source B to target schema
# =========================================================

def map_to_target_schema(df, tracker=None):

    df = df.copy()

    df = map_gender(df)

    result = pd.DataFrame({
        "SRC": df["src"],
        "PATIENT_ID": df["member_id"],
        "BIRTH_YEAR": df["birth_yr"],
        "GENDER": df["GENDER"],
        "ZIP3": df["zip3"],
        "CLAIM_ID": df["encounter_id"],
        "SERVICE_DATE": df["svc_date"],
        "DIAGNOSIS_CODE": df["dx_code"],
        "PLACE_OF_SERVICE": df["pos_code"],
        "RENDERING_NPI": df["rendering_npi"],
        "REFERRING_NPI": df["referring_npi"],
        "BILLING_NPI": df["billing_npi"],
        "PRIMARY_PLAN_ID": df["payer_primary"],
        "BILLED_AMOUNT": df["billed_amount"],
    })

    # Ensure the target order is explicit.
    result = result[TARGET_COLUMNS].copy()

    if tracker is not None:
        tracker.record(
            stage="Source B - Target schema mapping",
            rows_in=len(df),
            rows_out=len(result),
            reason="Mapped Source B fields to the common target schema"
        )

    return result


# =========================================================
# Stage 7: Final validation
# =========================================================

def validate_final_source_b(df):
    """
    Validate the transformed Source B dataset.
    """

    print("\n========== FINAL SOURCE B VALIDATION ==========")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumns:")
    print(df.columns.tolist())

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    missing_columns = [
        col
        for col in TARGET_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing target columns: {missing_columns}"
        )

    # -----------------------------------------------------
    # Validate diagnosis
    # -----------------------------------------------------

    if df["DIAGNOSIS_CODE"].isna().any():
        raise ValueError(
            "Missing diagnosis codes found."
        )

    # -----------------------------------------------------
    # Validate gender
    # -----------------------------------------------------

    invalid_gender = (
        set(df["GENDER"].dropna().unique())
        - {"M", "F"}
    )

    if invalid_gender:
        raise ValueError(
            f"Invalid gender values found: {invalid_gender}"
        )

    # -----------------------------------------------------
    # Validate grain
    # -----------------------------------------------------

    duplicate_mask = df.duplicated(
        subset=[
            "CLAIM_ID",
            "DIAGNOSIS_CODE"
        ],
        keep=False
    )

    duplicate_count = duplicate_mask.sum()

    print(
        "\nDuplicate CLAIM_ID + DIAGNOSIS_CODE rows:",
        duplicate_count
    )

    if duplicate_count > 0:
        raise ValueError(
            "Final Source B grain contains duplicates."
        )

    # -----------------------------------------------------
    # Validate source
    # -----------------------------------------------------

    print(
        "SRC values:",
        df["SRC"].unique().tolist()
    )

    if set(df["SRC"].dropna().unique()) != {"SRC_B"}:
        raise ValueError(
            "Unexpected SRC values found."
        )

    # -----------------------------------------------------
    # Sample
    # -----------------------------------------------------

    print("\nSample:")

    print(
        df[
            [
                "PATIENT_ID",
                "CLAIM_ID",
                "SERVICE_DATE",
                "BIRTH_YEAR",
                "GENDER",
                "DIAGNOSIS_CODE",
                "BILLED_AMOUNT",
                "SRC",
            ]
        ]
        .head(5)
        .to_string(index=False)
    )

    return df


# =========================================================
# Run Source B transformation
# =========================================================

def run_source_b(tracker):
    """
    Run the complete Source B transformation pipeline.

    This function can be used:
    1. Directly from source_b.py
    2. By the main pipeline/API later
    """

    source_b = load_source_b()

    print("========== SOURCE B ==========")
    print("Raw rows:", len(source_b))
    print("Raw columns:", len(source_b.columns))

    # -----------------------------------------------------
    # 1. Filter service dates
    # -----------------------------------------------------

    source_b = filter_service_dates(
        source_b,
        tracker
    )

    # -----------------------------------------------------
    # 2. Normalize diagnosis codes
    # -----------------------------------------------------

    source_b = normalize_diagnosis_codes(
        source_b,
        tracker
    )

    print("\n[Diagnosis normalization]")
    print("Rows:", len(source_b))

    # -----------------------------------------------------
    # 3. Validate Source B grain
    # -----------------------------------------------------

    source_b = enforce_source_b_grain(
        source_b,
        tracker
    )

    # -----------------------------------------------------
    # 4. Map to common target schema
    # -----------------------------------------------------

    source_b = map_to_target_schema(
        source_b,
        tracker
    )

    print("\n[Target schema mapping]")
    print("Rows:", len(source_b))
    print("Columns:", len(source_b.columns))

    print("\nColumns:")
    print(source_b.columns.tolist())

    # -----------------------------------------------------
    # 5. Final validation
    # -----------------------------------------------------

    source_b = validate_final_source_b(
        source_b
    )

    # -----------------------------------------------------
    # Save final Source B dataset
    # -----------------------------------------------------

    source_b.to_csv(
        "data/processed/source_b_final.csv",
        index=False
    )

    print("\n========== SOURCE B COMPLETE ==========")
    print("Final rows:", len(source_b))

    return source_b


# =========================================================
# Standalone execution
# =========================================================

if __name__ == "__main__":

    tracker = StageTracker()

    source_b = run_source_b(
        tracker
    )

    tracker.print_stages()