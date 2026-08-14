import pandas as pd

from src.stage_tracker import StageTracker


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

FILE_PATH = "data/raw/source_a_claims.csv.xlsx"

DIAGNOSIS_COLS = [
    "diagnosis_code_1",
    "diagnosis_code_2",
    "diagnosis_code_3",
    "diagnosis_code_4",
    "diagnosis_code_5",
    "diagnosis_code_6",
    "diagnosis_code_7",
    "diagnosis_code_8",
]

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


# ---------------------------------------------------------
# Stage 1: Load Source A
# ---------------------------------------------------------

def load_source_a():
    """Load the raw Source A dataset."""

    return pd.read_excel(FILE_PATH)


# ---------------------------------------------------------
# Stage 2: Remove missing patients
# ---------------------------------------------------------

def remove_missing_patients(df, tracker=None):
    """
    Remove rows where patient_id is missing.
    """

    rows_in = len(df)

    result = df.dropna(
        subset=["patient_id"]
    ).copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    print("\n[Missing patient filter]")
    print("Rows in:", rows_in)
    print("Rows out:", rows_out)
    print("Rows dropped:", rows_dropped)

    if tracker is not None:
        tracker.record(
            stage="Source A - Missing patient filter",
            rows_in=rows_in,
            rows_out=rows_out,
            reason="Dropped rows with missing PATIENT_ID"
        )

    return result


# ---------------------------------------------------------
# Stage 3: Filter service dates
# ---------------------------------------------------------

def filter_service_dates(df, tracker=None):
    """
    Convert service_from_date from YYYYMMDD integer
    into a proper date and keep only dates between
    2018-01-01 and 2025-02-28 inclusive.
    """

    df = df.copy()

    df["service_from_date"] = pd.to_datetime(
        df["service_from_date"].astype(str),
        format="%Y%m%d",
        errors="raise"
    )

    rows_in = len(df)

    result = df[
        (df["service_from_date"] >= START_DATE)
        & (df["service_from_date"] <= END_DATE)
    ].copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    if tracker is not None:
        tracker.record(
            stage="Source A - Service date filter",
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


# ---------------------------------------------------------
# Stage 4: Expand diagnosis columns
# ---------------------------------------------------------

def expand_diagnoses(df, tracker=None):
    """
    Convert the eight diagnosis columns into
    one diagnosis_code column.
    """

    id_cols = [
        col for col in df.columns
        if col not in DIAGNOSIS_COLS
    ]

    rows_in = len(df)

    result = df.melt(
        id_vars=id_cols,
        value_vars=DIAGNOSIS_COLS,
        var_name="diagnosis_position",
        value_name="diagnosis_code"
    )

    rows_out = len(result)

    if tracker is not None:
        tracker.record(
            stage="Source A - Diagnosis expansion",
            rows_in=rows_in,
            rows_out=rows_out,
            reason=(
                "Expanded multiple diagnosis columns "
                "into diagnosis-level rows"
            )
        )

    return result


# ---------------------------------------------------------
# Stage 5: Remove empty diagnoses
# ---------------------------------------------------------

def remove_empty_diagnoses(df, tracker=None):
    """
    Remove rows where the diagnosis slot is empty.
    """

    rows_in = len(df)

    result = df.dropna(
        subset=["diagnosis_code"]
    ).copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    if tracker is not None:
        tracker.record(
            stage="Source A - Empty diagnosis filter",
            rows_in=rows_in,
            rows_out=rows_out,
            reason="Dropped rows without a diagnosis code"
        )

    print("\n[Empty diagnosis filter]")
    print("Rows in:", rows_in)
    print("Rows out:", rows_out)
    print("Rows dropped:", rows_dropped)

    return result


# ---------------------------------------------------------
# Stage 6: Normalize diagnosis codes
# ---------------------------------------------------------

def normalize_diagnosis_codes(df):
    """
    Normalize diagnosis codes:
    - uppercase
    - remove dots
    """

    df = df.copy()

    df["diagnosis_code"] = (
        df["diagnosis_code"]
        .astype(str)
        .str.upper()
        .str.replace(".", "", regex=False)
    )

    return df


# ---------------------------------------------------------
# Stage 7: Enforce Source A grain
# ---------------------------------------------------------

def enforce_source_a_grain(df, tracker=None):
    """
    Keep one row per claim + diagnosis combination.

    Repeated diagnosis codes within the same claim are
    duplicate representations caused by multiple diagnosis
    positions in the source data.
    """

    rows_in = len(df)

    result = df.drop_duplicates(
        subset=[
            "claim_id",
            "diagnosis_code"
        ],
        keep="first"
    ).copy()

    rows_out = len(result)
    rows_dropped = rows_in - rows_out

    if tracker is not None:
        tracker.record(
            stage="Source A - Grain enforcement",
            rows_in=rows_in,
            rows_out=rows_out,
            reason=(
                "Removed repeated diagnosis codes "
                "within the same claim"
            )
        )

    print("\n[Source A grain enforcement]")
    print("Rows in:", rows_in)
    print("Rows out:", rows_out)
    print("Rows dropped:", rows_dropped)
    print("Grain: claim_id + diagnosis_code")

    return result


# ---------------------------------------------------------
# Stage 8: Map Source A to target schema
# ---------------------------------------------------------

def map_to_target_schema(df):
    """
    Rename Source A columns to the canonical target schema
    and create the SRC field.
    """

    result = df.copy()

    result = result.rename(
        columns={
            "patient_id": "PATIENT_ID",
            "patient_birth_year": "BIRTH_YEAR",
            "patient_gender": "GENDER",
            "patient_zip3": "ZIP3",
            "claim_id": "CLAIM_ID",
            "service_from_date": "SERVICE_DATE",
            "place_of_svc_cd": "PLACE_OF_SERVICE",
            "provider_rendering_id": "RENDERING_NPI",
            "provider_referring_id": "REFERRING_NPI",
            "provider_billing_id": "BILLING_NPI",
            "primary_plan_id": "PRIMARY_PLAN_ID",
            "bill_amt": "BILLED_AMOUNT",
            "diagnosis_code": "DIAGNOSIS_CODE",
        }
    )

    # Source A identifies itself as SRC_A.
    result["SRC"] = result["data_source"]

    return result


# ---------------------------------------------------------
# Run Source A transformation
# ---------------------------------------------------------

def run_source_a(tracker):
    """
    Run the complete Source A transformation pipeline.

    The same function can be used:
    1. Directly from source_a.py
    2. By the main pipeline/API later
    """

    source_a = load_source_a()

    print("========== SOURCE A ==========")
    print("Raw rows:", len(source_a))
    print("Raw columns:", len(source_a.columns))

    # 1. Remove missing patients
    source_a = remove_missing_patients(
        source_a,
        tracker
    )

    # 2. Filter service dates
    source_a = filter_service_dates(
        source_a,
        tracker
    )

    # 3. Expand diagnosis columns
    source_a = expand_diagnoses(
        source_a,
        tracker
    )

    print("\n[Diagnosis expansion]")
    print("Rows after expansion:", len(source_a))

    # 4. Remove empty diagnoses
    source_a = remove_empty_diagnoses(
        source_a,
        tracker
    )

    # 5. Normalize diagnosis codes
    source_a = normalize_diagnosis_codes(
        source_a
    )

    print("\n[Diagnosis normalization]")
    print("Rows:", len(source_a))

    # 6. Enforce required grain
    source_a = enforce_source_a_grain(
        source_a,
        tracker
    )

    # 7. Map to target schema
    source_a = map_to_target_schema(
        source_a
    )

    # -----------------------------------------------------
    # Keep only required target columns
    # -----------------------------------------------------

    source_a = source_a[
        TARGET_COLUMNS
    ].copy()

    print("\n[Target schema mapping]")
    print("Rows:", len(source_a))
    print("Columns:", len(source_a.columns))

    print("\nColumns:")
    print(source_a.columns.tolist())

    print("\n[Current Source A dataset]")
    print("Rows:", len(source_a))

    print("\nSample:")
    print(
        source_a[
            [
                "CLAIM_ID",
                "DIAGNOSIS_CODE",
                "SERVICE_DATE",
                "PATIENT_ID",
                "BILLED_AMOUNT",
                "SRC",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    # Save final transformed Source A dataset
    source_a.to_csv(
        "data/processed/source_a_final.csv",
        index=False
    )

    return source_a


# ---------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------

if __name__ == "__main__":

    tracker = StageTracker()

    source_a = run_source_a(
        tracker
    )

    print("\n[Top 5 rows]")
    print(
        source_a
        .head(5)
        .to_string(index=False)
    )

    tracker.print_stages()