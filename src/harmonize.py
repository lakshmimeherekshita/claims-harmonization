import pandas as pd

from src.stage_tracker import StageTracker


# =========================================================
# FILE PATHS
# =========================================================

SOURCE_A_PATH = "data/processed/source_a_final.csv"
SOURCE_B_PATH = "data/processed/source_b_final.csv"
SOURCE_C_PATH = "data/processed/source_c_final.csv"

DICTIONARY_PATH = "data/raw/dx_dictionary.csv.xlsx"

COMBINED_OUTPUT_PATH = "data/processed/combined_claims.csv"
FINAL_OUTPUT_PATH = "data/processed/final_harmonized_claims.csv"


# =========================================================
# EXPECTED TARGET SCHEMA
# =========================================================

EXPECTED_COLUMNS = [
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
# LOAD PROCESSED SOURCE DATASETS
# =========================================================

def load_processed_sources():

    source_a = pd.read_csv(
        SOURCE_A_PATH
    )

    source_b = pd.read_csv(
        SOURCE_B_PATH
    )

    source_c = pd.read_csv(
        SOURCE_C_PATH
    )

    return source_a, source_b, source_c


# =========================================================
# LOAD DIAGNOSIS DICTIONARY
# =========================================================

def load_dictionary():

    dictionary = pd.read_excel(
        DICTIONARY_PATH
    )

    return dictionary


# =========================================================
# STANDARDIZE DATA TYPES
# =========================================================

def standardize_dtypes(df):

    df = df.copy()

    # Birth year
    df["BIRTH_YEAR"] = (
        df["BIRTH_YEAR"]
        .astype("int64")
    )

    # ZIP3
    df["ZIP3"] = (
        df["ZIP3"]
        .astype("int64")
    )

    # Service date
    df["SERVICE_DATE"] = pd.to_datetime(
        df["SERVICE_DATE"],
        errors="raise"
    )

    return df


def standardize_all_sources(
    source_a,
    source_b,
    source_c,
    tracker=None
):

    source_a = standardize_dtypes(
        source_a
    )

    source_b = standardize_dtypes(
        source_b
    )

    source_c = standardize_dtypes(
        source_c
    )

    if tracker is not None:

        rows_total = (
            len(source_a)
            + len(source_b)
            + len(source_c)
        )

        tracker.record(
            stage=(
                "Harmonization - "
                "Data type standardization"
            ),
            rows_in=rows_total,
            rows_out=rows_total,
            reason=(
                "Standardized BIRTH_YEAR, ZIP3, "
                "and SERVICE_DATE data types"
            )
        )

    return (
        source_a,
        source_b,
        source_c
    )


# =========================================================
# SOURCE SCHEMA VALIDATION
# =========================================================

def validate_source_schema(
    df,
    source_name
):

    if df.columns.tolist() != EXPECTED_COLUMNS:

        raise ValueError(
            f"{source_name} columns do not match "
            f"expected schema.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Actual: {df.columns.tolist()}"
        )


def validate_all_source_schemas(
    source_a,
    source_b,
    source_c,
    tracker=None
):

    validate_source_schema(
        source_a,
        "Source A"
    )

    validate_source_schema(
        source_b,
        "Source B"
    )

    validate_source_schema(
        source_c,
        "Source C"
    )

    print(
        "[Schema validation] "
        "All source schemas match."
    )

    if tracker is not None:

        rows_total = (
            len(source_a)
            + len(source_b)
            + len(source_c)
        )

        tracker.record(
            stage=(
                "Harmonization - "
                "Source schema validation"
            ),
            rows_in=rows_total,
            rows_out=rows_total,
            reason=(
                "Validated all source datasets "
                "against the common target schema"
            )
        )


# =========================================================
# COMBINE SOURCES
# =========================================================

def combine_sources(
    source_a,
    source_b,
    source_c,
    tracker=None
):

    combined = pd.concat(
        [
            source_a,
            source_b,
            source_c
        ],
        ignore_index=True
    )

    print(
        "\n========== COMBINED SOURCES =========="
    )

    print(
        "Source A rows:",
        len(source_a)
    )

    print(
        "Source B rows:",
        len(source_b)
    )

    print(
        "Source C rows:",
        len(source_c)
    )

    print(
        "Combined rows:",
        len(combined)
    )

    if tracker is not None:

        rows_total = (
            len(source_a)
            + len(source_b)
            + len(source_c)
        )

        tracker.record(
            stage=(
                "Harmonization - "
                "Source combination"
            ),
            rows_in=rows_total,
            rows_out=len(combined),
            reason=(
                "Concatenated validated Source A, "
                "Source B, and Source C datasets"
            )
        )

    return combined


# =========================================================
# COMBINED DATASET VALIDATION
# =========================================================

def validate_combined(
    combined,
    tracker=None
):

    print(
        "\n========== "
        "COMBINED DATASET VALIDATION =========="
    )

    print(
        "Rows:",
        len(combined)
    )

    print(
        "Columns:",
        len(combined.columns)
    )

    print("\nSRC distribution:")

    print(
        combined["SRC"].value_counts()
    )

    print("\nMissing values:")

    print(
        combined.isna().sum()
    )

    duplicate_count = combined.duplicated(
        subset=[
            "SRC",
            "CLAIM_ID",
            "DIAGNOSIS_CODE"
        ],
        keep=False
    ).sum()

    print(
        "\nDuplicate "
        "SRC + CLAIM_ID + DIAGNOSIS_CODE:",
        duplicate_count
    )

    if duplicate_count > 0:

        raise ValueError(
            "Combined dataset contains duplicate "
            "SRC + CLAIM_ID + DIAGNOSIS_CODE records."
        )

    if tracker is not None:

        tracker.record(
            stage=(
                "Harmonization - "
                "Combined dataset validation"
            ),
            rows_in=len(combined),
            rows_out=len(combined),
            reason=(
                "Validated combined row count, "
                "missing values, and "
                "SRC + CLAIM_ID + DIAGNOSIS_CODE grain"
            )
        )

    return combined


# =========================================================
# ADD DIAGNOSIS DESCRIPTION
# =========================================================

def add_diagnosis_description(
    combined,
    dictionary,
    tracker=None
):

    print(
        "\n========== "
        "DIAGNOSIS DICTIONARY JOIN =========="
    )

    rows_before = len(combined)

    # -----------------------------------------------------
    # Keep only required dictionary columns
    # -----------------------------------------------------

    dictionary_lookup = dictionary[
        [
            "dx_code",
            "dx_description"
        ]
    ].copy()

    # -----------------------------------------------------
    # Normalize dictionary diagnosis codes
    # -----------------------------------------------------

    dictionary_lookup["dx_code"] = (
        dictionary_lookup["dx_code"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(
            ".",
            "",
            regex=False
        )
    )

    # -----------------------------------------------------
    # Validate dictionary key uniqueness
    # -----------------------------------------------------

    duplicate_codes = (
        dictionary_lookup
        .duplicated(
            subset=["dx_code"],
            keep=False
        )
        .sum()
    )

    if duplicate_codes > 0:

        raise ValueError(
            "Duplicate diagnosis codes found "
            "in dictionary."
        )

    # -----------------------------------------------------
    # LEFT JOIN
    # -----------------------------------------------------

    result = combined.merge(
        dictionary_lookup,
        how="left",
        left_on="DIAGNOSIS_CODE",
        right_on="dx_code",
        validate="many_to_one"
    )

    # -----------------------------------------------------
    # Remove temporary dictionary key
    # -----------------------------------------------------

    result = result.drop(
        columns=["dx_code"]
    )

    # -----------------------------------------------------
    # Rename description
    # -----------------------------------------------------

    result = result.rename(
        columns={
            "dx_description": "DIAGNOSIS_DESC"
        }
    )

    rows_after = len(result)

    print(
        "Rows before join:",
        rows_before
    )

    print(
        "Rows after join:",
        rows_after
    )

    # -----------------------------------------------------
    # LEFT JOIN must preserve row count
    # -----------------------------------------------------

    if rows_after != rows_before:

        raise ValueError(
            "Dictionary LEFT JOIN changed "
            "the number of rows."
        )

    missing_description = (
        result["DIAGNOSIS_DESC"]
        .isna()
        .sum()
    )

    print(
        "Rows with missing DIAGNOSIS_DESC:",
        missing_description
    )

    print(
        "\nUnmatched diagnosis codes:"
    )

    print(
        result.loc[
            result["DIAGNOSIS_DESC"].isna(),
            "DIAGNOSIS_CODE"
        ]
        .value_counts()
        .sort_index()
    )

    if tracker is not None:

        tracker.record(
            stage=(
                "Harmonization - "
                "Diagnosis dictionary join"
            ),
            rows_in=rows_before,
            rows_out=rows_after,
            reason=(
                "LEFT JOINed diagnosis descriptions "
                "using DIAGNOSIS_CODE"
            )
        )

    return result


# =========================================================
# RUN HARMONIZATION
# =========================================================

def run_harmonization(
    source_a=None,
    source_b=None,
    source_c=None,
    tracker=None
):
    """
    Run the complete harmonization pipeline.

    If source datasets are provided, they are used directly.

    If they are not provided, the already transformed
    Source A, B, and C CSV files are loaded from disk.

    This allows the same function to be used:
        1. Standalone from harmonize.py
        2. By pipeline.py later
        3. By the API later
    """

    # -----------------------------------------------------
    # Create tracker only when running standalone
    # -----------------------------------------------------

    if tracker is None:
        tracker = StageTracker()

    # -----------------------------------------------------
    # Load processed sources if not supplied
    # -----------------------------------------------------

    if (
        source_a is None
        or source_b is None
        or source_c is None
    ):

        (
            source_a,
            source_b,
            source_c
        ) = load_processed_sources()

    # -----------------------------------------------------
    # Validate source schemas
    # -----------------------------------------------------

    validate_all_source_schemas(
        source_a,
        source_b,
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # Standardize common data types
    # -----------------------------------------------------

    (
        source_a,
        source_b,
        source_c
    ) = standardize_all_sources(
        source_a,
        source_b,
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # Combine sources
    # -----------------------------------------------------

    combined = combine_sources(
        source_a,
        source_b,
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # Validate combined dataset
    # -----------------------------------------------------

    combined = validate_combined(
        combined,
        tracker
    )

    # -----------------------------------------------------
    # Save intermediate combined dataset
    # -----------------------------------------------------

    combined.to_csv(
        COMBINED_OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # Load diagnosis dictionary
    # -----------------------------------------------------

    dictionary = load_dictionary()

    # -----------------------------------------------------
    # LEFT JOIN diagnosis description
    # -----------------------------------------------------

    final_data = add_diagnosis_description(
        combined,
        dictionary,
        tracker
    )

    # -----------------------------------------------------
    # Save final harmonized dataset
    # -----------------------------------------------------

    final_data.to_csv(
        FINAL_OUTPUT_PATH,
        index=False
    )

    # -----------------------------------------------------
    # Return final data + tracker
    # -----------------------------------------------------

    return final_data, tracker


# =========================================================
# STANDALONE EXECUTION
# =========================================================

if __name__ == "__main__":

    final_data, tracker = run_harmonization()

    print(
        "\nCombined dataset saved to:"
    )

    print(
        COMBINED_OUTPUT_PATH
    )

    print(
        "\nFinal harmonized dataset saved to:"
    )

    print(
        FINAL_OUTPUT_PATH
    )

    print(
        "\n========== "
        "HARMONIZATION COMPLETE =========="
    )

    print(
        "Final rows:",
        len(final_data)
    )

    print(
        "Final columns:",
        len(final_data.columns)
    )

    tracker.print_stages()