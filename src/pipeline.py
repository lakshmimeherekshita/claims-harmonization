import os
from src.stage_tracker import StageTracker

from src.source_a import run_source_a
from src.source_b import run_source_b
from src.source_c import run_source_c
from src.harmonize import run_harmonization


def run_pipeline():
    os.makedirs("data/processed", exist_ok=True)
    """
    Run the complete claims harmonization pipeline
    using one shared StageTracker.
    """

    # One tracker for the entire pipeline run
    tracker = StageTracker()

    print("\n========================================")
    print("        CLAIMS HARMONIZATION PIPELINE")
    print("========================================")

    # -----------------------------------------------------
    # Source A
    # -----------------------------------------------------

    print("\n========== RUNNING SOURCE A ==========")

    source_a = run_source_a(
        tracker
    )

    print(
        "\nSource A completed.",
        "Rows:",
        len(source_a)
    )

    # -----------------------------------------------------
    # Source B
    # -----------------------------------------------------

    print("\n========== RUNNING SOURCE B ==========")

    source_b = run_source_b(
        tracker
    )

    print(
        "\nSource B completed.",
        "Rows:",
        len(source_b)
    )

    # -----------------------------------------------------
    # Source C
    # -----------------------------------------------------

    print("\n========== RUNNING SOURCE C ==========")

    source_c = run_source_c(
        tracker
    )

    print(
        "\nSource C completed.",
        "Rows:",
        len(source_c)
    )

    # -----------------------------------------------------
    # Harmonization
    # -----------------------------------------------------

    print(
        "\n========== RUNNING HARMONIZATION =========="
    )

    final_data, _ = run_harmonization(
        source_a,
        source_b,
        source_c,
        tracker
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "       COMPLETE PIPELINE FINISHED"
    )

    print(
        "========================================"
    )

    print(
        "Final rows:",
        len(final_data)
    )

    print(
        "Final columns:",
        len(final_data.columns)
    )

    # -----------------------------------------------------
    # Print ALL stages from the same tracker
    # -----------------------------------------------------

    tracker.print_stages()

    return final_data, tracker


# =========================================================
# Standalone execution
# =========================================================

if __name__ == "__main__":

    final_data, tracker = run_pipeline()