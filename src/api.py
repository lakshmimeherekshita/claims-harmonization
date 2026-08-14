import hashlib
import uuid
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.pipeline import run_pipeline


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Claims Harmonization API",
    description="Multi-Source Claims Harmonization Pipeline",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# RUN STORE
# =========================================================

# Stores information about completed pipeline runs.
# This is sufficient for the assignment.
runs = {}


# =========================================================
# CONFIGURATION
# =========================================================

FINAL_OUTPUT_PATH = (
    "data/processed/final_harmonized_claims.csv"
)


# =========================================================
# HELPER: SHA256
# =========================================================

def calculate_file_hash(path):
    """
    Calculate SHA256 hash of a file.
    Used for reproducibility checking.
    """

    sha256 = hashlib.sha256()

    with open(path, "rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


# =========================================================
# HELPER: LOAD FINAL DATASET
# =========================================================

def load_final_data():

    return pd.read_csv(
        FINAL_OUTPUT_PATH
    )


# =========================================================
# POST /run
# =========================================================

@app.post("/run")
def run_claims_pipeline():
    """
    Run the complete claims harmonization pipeline
    and return a unique run ID.
    """

    run_id = str(uuid.uuid4())

    started_at = datetime.now()

    try:

        final_data, tracker = run_pipeline()

        finished_at = datetime.now()

        output_hash = calculate_file_hash(
            FINAL_OUTPUT_PATH
        )

        runs[run_id] = {
            "run_id": run_id,
            "status": "completed",
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "rows": len(final_data),
            "columns": len(final_data.columns),
            "tracker": tracker,
            "output_hash": output_hash,
        }

        return {
            "run_id": run_id,
            "status": "completed",
            "rows": len(final_data),
            "columns": len(final_data.columns),
        }

    except Exception as exc:

        runs[run_id] = {
            "run_id": run_id,
            "status": "failed",
            "error": str(exc),
        }

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# =========================================================
# GET /run/{id}/stages
# =========================================================

@app.get("/run/{run_id}/stages")
def get_run_stages(run_id: str):
    """
    Return the stage-by-stage history for a run.
    """

    if run_id not in runs:

        raise HTTPException(
            status_code=404,
            detail="Run ID not found."
        )

    run = runs[run_id]

    if run["status"] != "completed":

        raise HTTPException(
            status_code=400,
            detail="This pipeline run failed."
        )

    tracker = run["tracker"]

    return {
        "run_id": run_id,
        "stages": tracker.get_stages(),
    }


# =========================================================
# GET /run/{id}/validate
# =========================================================


@app.get("/run/{run_id}/validate")
def validate_run(run_id: str):
    """
    Run all assignment acceptance checks and return
    PASS / FAIL for each check.
    """

    if run_id not in runs:
        raise HTTPException(
            status_code=404,
            detail="Run ID not found."
        )

    run = runs[run_id]

    if run["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="This pipeline run failed."
        )

    final_data = load_final_data()

    checks = []

    # =====================================================
    # CHECK 1
    # =====================================================

    actual = len(final_data)
    expected = 159704

    checks.append({
        "check": "Total rows in the final output",
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual == expected else "FAIL",
    })

    # =====================================================
    # CHECK 2
    # =====================================================

    actual = int(final_data["CLAIM_ID"].nunique())
    expected = 68205

    checks.append({
        "check": "Distinct claims across all sources",
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual == expected else "FAIL",
    })

    # =====================================================
    # CHECK 3
    # =====================================================

    actual = int(final_data["PATIENT_ID"].nunique())
    expected = 11963

    checks.append({
        "check": "Distinct patients",
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual == expected else "FAIL",
    })

    # =====================================================
    # CHECK 4
    # =====================================================

    actual = int(final_data["DIAGNOSIS_CODE"].nunique())
    expected = 44

    checks.append({
        "check": "Distinct diagnosis codes",
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual == expected else "FAIL",
    })

    # =====================================================
    # CHECK 5
    # =====================================================

    patient = final_data[
        final_data["PATIENT_ID"] == "P00042"
    ]

    actual = int(patient["DIAGNOSIS_CODE"].nunique())
    expected = 7

    checks.append({
        "check": (
            "Patient P00042 — "
            "distinct diagnosis codes"
        ),
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual == expected else "FAIL",
    })

    # =====================================================
    # CHECK 6
    # =====================================================

    actual = len(patient)
    expected = 7

    checks.append({
        "check": "Patient P00042 — total rows",
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual == expected else "FAIL",
    })

    # =====================================================
    # CHECK 7
    # =====================================================

    diagnosis_codes = (
        final_data["DIAGNOSIS_CODE"]
        .dropna()
        .astype(str)
    )

    contains_dot = bool(
        diagnosis_codes
        .str.contains(".", regex=False)
        .any()
    )

    all_uppercase = bool(
        (
            diagnosis_codes
            == diagnosis_codes.str.upper()
        ).all()
    )

    actual = bool(
        not contains_dot
        and all_uppercase
    )

    expected = True

    checks.append({
        "check": (
            "No DIAGNOSIS_CODE contains a dot; "
            "all uppercase"
        ),
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual else "FAIL",
    })

    # =====================================================
    # CHECK 8
    # =====================================================

    service_dates = pd.to_datetime(
        final_data["SERVICE_DATE"],
        errors="coerce"
    )

    actual = bool(
        service_dates.notna().all()
        and
        service_dates.between(
            "2018-01-01",
            "2025-02-28"
        ).all()
    )

    expected = True

    checks.append({
        "check": (
            "All SERVICE_DATE between "
            "2018-01-01 and 2025-02-28"
        ),
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual else "FAIL",
    })

    # =====================================================
    # CHECK 9
    # =====================================================

    patient_ids = final_data["PATIENT_ID"]

    actual = bool(
        patient_ids.notna().all()
        and
        patient_ids.astype(str)
        .str.strip()
        .ne("")
        .all()
    )

    expected = True

    checks.append({
        "check": "No row has an empty PATIENT_ID",
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual else "FAIL",
    })

    # =====================================================
    # CHECK 10
    # =====================================================

    previous_run = None

    completed_runs = [
        stored_run
        for stored_run in runs.values()
        if (
            stored_run["status"] == "completed"
            and stored_run["run_id"] != run_id
        )
    ]

    if completed_runs:
        previous_run = completed_runs[-1]

    if previous_run is None:

        actual = False

        detail = (
            "No previous completed run exists. "
            "Run the pipeline again and validate the "
            "second run to establish consecutive-run "
            "reproducibility."
        )

    else:

        actual = bool(
            run["output_hash"]
            == previous_run["output_hash"]
        )

        detail = (
            f"Compared SHA256 with previous run "
            f"{previous_run['run_id']}."
        )

    expected = True

    checks.append({
        "check": (
            "Two consecutive runs produce "
            "identical output"
        ),
        "expected": expected,
        "actual": actual,
        "status": "PASS" if actual else "FAIL",
        "detail": detail,
    })

    # =====================================================
    # OVERALL RESULT
    # =====================================================

    all_passed = all(
        check["status"] == "PASS"
        for check in checks
    )

    return {
        "run_id": run_id,
        "overall": "PASS" if all_passed else "FAIL",
        "checks": checks,
    }

# =========================================================
# GET /summary
# =========================================================

@app.get("/summary")
def get_summary():
    """
    Return final row and claim counts per source.
    """

    final_data = load_final_data()

    source_summary = []

    for source in [
        "SRC_A",
        "SRC_B",
        "SRC_C"
    ]:

        source_data = final_data[
            final_data["SRC"] == source
        ]

        source_summary.append({
            "source": source,
            "rows": len(source_data),
            "distinct_claims": (
                source_data["CLAIM_ID"]
                .nunique()
            ),
        })

    return {
        "final_rows": len(final_data),
        "distinct_claims": (
            final_data["CLAIM_ID"]
            .nunique()
        ),
        "distinct_patients": (
            final_data["PATIENT_ID"]
            .nunique()
        ),
        "sources": source_summary,
    }