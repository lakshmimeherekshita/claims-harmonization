import pandas as pd

from src.stage_tracker import StageTracker


# =========================================================
# Configuration
# =========================================================

FILE_PATH = "data/raw/source_c_claims.csv.xlsx"

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
# Stage 1: Load Source C
# =========================================================

def load_source_c():
    """Load the raw Source C dataset."""

    return pd.read_excel(FILE_PATH)


# =========================================================
# Stage 2: Keep latest version per claim
# =========================================================

def keep_latest_version(df, tracker=None):
    """
    Source C can contain multiple versions of the same
    underlying claim_ref.

    For each claim_ref, retain only the rows belonging
    to its highest available version.
    """

    df = df.copy()

    rows_in = len(df)

    # Validate version values before using them
    if df["version"].isna().any():
        raise ValueError(
            "Missing version values found in Source C."
        )

    # Find the latest version available for each claim
    latest_version = (
        df.groupby("claim_ref")["version"]
        .transform("max")
    )

    # Keep only rows belonging to the latest version
    result = df[
        df["version"] == latest_version
    ].copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    if tracker is not None:
        tracker.record(
            stage="Source C - Latest version selection",
            rows_in=rows_in,
            rows_out=rows_out,
            reason=(
                "Retained the highest version for each claim_ref; "
                "superseded claim versions were removed"
            )
        )

    print("\n[Latest version selection]")
    print("Rows in:", rows_in)
    print("Rows out:", rows_out)
    print("Rows dropped:", rows_dropped)

    print("\nVersions retained:")
    print(
        result["version"]
        .value_counts()
        .sort_index()
    )

    print(
        "\nDistinct claim_ref retained:",
        result["claim_ref"].nunique()
    )

    return result


# =========================================================
# Stage 3: Create final claim ID
# =========================================================

def create_claim_id(df):
    """
    After latest-version selection, each claim_ref has
    only one retained version.

    The final CLAIM_ID is the underlying claim_ref.
    """

    df = df.copy()

    df["CLAIM_ID"] = (
        df["claim_ref"]
        .astype(str)
        .str.strip()
    )

    return df


# =========================================================
# Stage 4: Filter service dates
# =========================================================

def filter_service_dates(df, tracker=None):
    """
    Keep only records with service dates between
    2018-01-01 and 2025-02-28 inclusive.
    """

    df = df.copy()

    rows_in = len(df)

    df["date_of_service"] = pd.to_datetime(
        df["date_of_service"],
        errors="raise"
    )

    valid_date = (
        (df["date_of_service"] >= START_DATE)
        & (df["date_of_service"] <= END_DATE)
    )

    result = df[valid_date].copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    if tracker is not None:
        tracker.record(
            stage="Source C - Service date filter",
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
# Stage 5: Expand diagnosis codes
# =========================================================

def expand_diagnosis_codes(df, tracker=None):
    """
    Source C stores multiple diagnosis codes in one
    pipe-separated column.

    Example:
        E119|I10|J449

    becomes three diagnosis-level rows.
    """

    df = df.copy()

    rows_before = len(df)

    df["diagnosis_codes"] = (
        df["diagnosis_codes"]
        .astype(str)
        .str.split("|")
    )

    df = df.explode(
        "diagnosis_codes"
    ).copy()

    rows_after = len(df)

    if tracker is not None:
        tracker.record(
            stage="Source C - Diagnosis expansion",
            rows_in=rows_before,
            rows_out=rows_after,
            reason=(
                "Expanded pipe-separated diagnosis codes "
                "into diagnosis-level rows"
            )
        )

    print("\n[Diagnosis expansion]")
    print("Rows before expansion:", rows_before)
    print("Rows after expansion:", rows_after)

    return df


# =========================================================
# Stage 6: Normalize diagnosis codes
# =========================================================

def normalize_diagnosis_codes(df, tracker=None):
    """
    Normalize diagnosis codes by:
    - trimming whitespace
    - converting to uppercase
    - removing dots
    """

    df = df.copy()

    df["DIAGNOSIS_CODE"] = (
        df["diagnosis_codes"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "", regex=False)
    )

    if tracker is not None:
        tracker.record(
            stage="Source C - Diagnosis normalization",
            rows_in=len(df),
            rows_out=len(df),
            reason=(
                "Normalized diagnosis codes by trimming whitespace, "
                "converting to uppercase, and removing dots"
            )
        )

    return df


# =========================================================
# Stage 7: Validate final diagnosis grain
# =========================================================

def validate_grain(df, tracker=None):
    """
    Final Source C grain:

        CLAIM_ID + DIAGNOSIS_CODE

    Do not silently drop duplicates.
    Raise an error if the established grain is violated.
    """

    duplicate_mask = df.duplicated(
        subset=[
            "CLAIM_ID",
            "DIAGNOSIS_CODE"
        ],
        keep=False
    )

    duplicate_rows = df[duplicate_mask]

    print("\n[Source C grain validation]")
    print(
        "Rows at diagnosis level:",
        len(df)
    )
    print(
        "Rows involved in duplicate "
        "CLAIM_ID + DIAGNOSIS_CODE:",
        len(duplicate_rows)
    )

    if len(duplicate_rows) > 0:

        print("\nDuplicate examples:")

        print(
            duplicate_rows[
                [
                    "CLAIM_ID",
                    "DIAGNOSIS_CODE",
                    "claim_ref",
                    "version"
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

        raise ValueError(
            "Source C contains duplicate "
            "CLAIM_ID + DIAGNOSIS_CODE combinations."
        )

    print("Grain validation passed.")
    print("Grain: CLAIM_ID + DIAGNOSIS_CODE")

    if tracker is not None:
        tracker.record(
            stage="Source C - Grain validation",
            rows_in=len(df),
            rows_out=len(df),
            reason=(
                "Validated CLAIM_ID + DIAGNOSIS_CODE grain; "
                "no duplicates found"
            )
        )

    return df


# =========================================================
# Stage 8: Map gender
# =========================================================

def map_gender(df):
    """
    Source C provides explicit gender values:

        Male   -> M
        Female -> F
    """

    df = df.copy()

    gender_mapping = {
        "Male": "M",
        "Female": "F"
    }

    df["GENDER"] = df["sex"].map(
        gender_mapping
    )

    if df["GENDER"].isna().any():

        invalid_values = (
            df.loc[
                df["GENDER"].isna(),
                "sex"
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            f"Unexpected gender values found: "
            f"{invalid_values}"
        )

    return df


# =========================================================
# Stage 9: Map Source C to target schema
# =========================================================

def map_to_target_schema(df, tracker=None):
    """
    Map Source C fields to the common target schema.
    """

    df = df.copy()

    df = map_gender(df)

    result = pd.DataFrame({
        "SRC": df["source_system"],
        "PATIENT_ID": df["pt_ref"],
        "BIRTH_YEAR": df["yob"],
        "GENDER": df["GENDER"],
        "ZIP3": df["zip_3"],
        "CLAIM_ID": df["CLAIM_ID"],
        "SERVICE_DATE": df["date_of_service"],
        "DIAGNOSIS_CODE": df["DIAGNOSIS_CODE"],
        "PLACE_OF_SERVICE": df["service_place"],
        "RENDERING_NPI": df["npi_rendering"],
        "REFERRING_NPI": df["npi_referring"],
        "BILLING_NPI": df["npi_billing"],
        "PRIMARY_PLAN_ID": df["plan_1"],
        "BILLED_AMOUNT": df["amount_billed"],
    })

    # Explicitly enforce target column order
    result = result[TARGET_COLUMNS].copy()

    if tracker is not None:
        tracker.record(
            stage="Source C - Target schema mapping",
            rows_in=len(df),
            rows_out=len(result),
            reason="Mapped Source C fields to the common target schema"
        )

    return result


# =========================================================
# Stage 10: Final validation
# =========================================================

def validate_final_source_c(df):

    print(
        "\n========== FINAL SOURCE C VALIDATION =========="
    )

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumns:")
    print(df.columns.tolist())

    # -----------------------------------------------------
    # Validate target schema
    # -----------------------------------------------------

    if df.columns.tolist() != TARGET_COLUMNS:

        raise ValueError(
            "Final Source C columns do not match "
            "the expected target schema."
        )

    # -----------------------------------------------------
    # Required diagnosis check
    # -----------------------------------------------------

    if df["DIAGNOSIS_CODE"].isna().any():

        raise ValueError(
            "Missing diagnosis codes found."
        )

    # -----------------------------------------------------
    # Gender validation
    # -----------------------------------------------------

    invalid_gender = (
        set(df["GENDER"].dropna().unique())
        - {"M", "F"}
    )

    if invalid_gender:

        raise ValueError(
            f"Invalid gender values found: "
            f"{invalid_gender}"
        )

    # -----------------------------------------------------
    # Final grain validation
    # -----------------------------------------------------

    duplicate_count = df.duplicated(
        subset=[
            "CLAIM_ID",
            "DIAGNOSIS_CODE"
        ],
        keep=False
    ).sum()

    print(
        "\nDuplicate CLAIM_ID + DIAGNOSIS_CODE rows:",
        duplicate_count
    )

    if duplicate_count > 0:

        raise ValueError(
            "Final Source C grain contains duplicates."
        )

    # -----------------------------------------------------
    # Source validation
    # -----------------------------------------------------

    print(
        "SRC values:",
        df["SRC"].unique().tolist()
    )

    if set(
        df["SRC"].dropna().unique()
    ) != {"SRC_C"}:

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
# Run Source C transformation
# =========================================================

def run_source_c(tracker):
    """
    Run the complete Source C transformation pipeline.

    This function can be used:
    1. Directly from source_c.py
    2. By the main pipeline/API later
    """

    source_c = load_source_c()

    print("========== SOURCE C ==========")
    print("Raw rows:", len(source_c))
    print("Raw columns:", len(source_c.columns))

    # -----------------------------------------------------
    # 1. Keep latest version for each claim_ref
    # -----------------------------------------------------

    source_c = keep_latest_version(
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # 2. Create final CLAIM_ID
    # -----------------------------------------------------

    source_c = create_claim_id(
        source_c
    )

    # -----------------------------------------------------
    # 3. Filter service dates
    # -----------------------------------------------------

    source_c = filter_service_dates(
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # 4. Expand pipe-separated diagnoses
    # -----------------------------------------------------

    source_c = expand_diagnosis_codes(
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # 5. Normalize diagnosis codes
    # -----------------------------------------------------

    source_c = normalize_diagnosis_codes(
        source_c,
        tracker
    )

    print("\n[Diagnosis normalization]")
    print("Rows:", len(source_c))
    print(
        "Unique diagnosis codes:",
        source_c["DIAGNOSIS_CODE"].nunique()
    )

    # -----------------------------------------------------
    # 6. Validate final diagnosis grain
    # -----------------------------------------------------

    source_c = validate_grain(
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # 7. Map to common target schema
    # -----------------------------------------------------

    source_c = map_to_target_schema(
        source_c,
        tracker
    )

    print("\n[Target schema mapping]")
    print("Rows:", len(source_c))
    print("Columns:", len(source_c.columns))

    print("\nColumns:")
    print(source_c.columns.tolist())

    # -----------------------------------------------------
    # 8. Final validation
    # -----------------------------------------------------

    source_c = validate_final_source_c(
        source_c
    )

    # -----------------------------------------------------
    # Save final Source C dataset
    # -----------------------------------------------------

    source_c.to_csv(
        "data/processed/source_c_final.csv",
        index=False
    )

    print("\n========== SOURCE C COMPLETE ==========")
    print("Final rows:", len(source_c))

    return source_c


# =========================================================
# Standalone execution
# =========================================================

if __name__ == "__main__":

    tracker = StageTracker()

    source_c = run_source_c(
        tracker
    )

    tracker.print_stages()