class StageTracker:
    """
    Stores row counts and drop reasons for every pipeline stage.
    """

    def __init__(self):
        self.stages = []

    def record(
        self,
        stage,
        rows_in,
        rows_out,
        reason="",
    ):
        rows_change = rows_out - rows_in

        self.stages.append({
            "stage": stage,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "rows_change": rows_change,
            "reason": reason
        })

    def get_stages(self):
        return self.stages

    def print_stages(self):
        print("\n========== PIPELINE STAGES ==========")

        for stage in self.stages:
            print(
                f"{stage['stage']} | "
                f"In: {stage['rows_in']} | "
                f"Out: {stage['rows_out']} | "
                f"Change: {stage['rows_change']:+d} | "
                f"Reason: {stage['reason']}"
            )