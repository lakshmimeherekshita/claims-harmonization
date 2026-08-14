# import pandas as pd

# # # file_path = "data/raw/source_a_claims.csv.xlsx"



# # # df = pd.read_excel(file_path)
# # # diagnosis_cols = [
# # #     "diagnosis_code_1",
# # #     "diagnosis_code_2",
# # #     "diagnosis_code_3",
# # #     "diagnosis_code_4",
# # #     "diagnosis_code_5",
# # #     "diagnosis_code_6",
# # #     "diagnosis_code_7",
# # #     "diagnosis_code_8"
# # # ]
# # # duplicate_diagnosis = df[
# # #     df["diagnosis_code_1"].notna() &
# # #     (df["diagnosis_code_1"] == df["diagnosis_code_2"])
# # # ]

# # # print(duplicate_diagnosis[
# # #     ["claim_id", "service_nbr", "diagnosis_code_1", "diagnosis_code_2"]
# # # ].head(20))

# # # print("Number of rows:", len(duplicate_diagnosis))

# # # print(df[diagnosis_cols].head(10))
# # # for i in range(1, 8):
# # #     current_col = f"diagnosis_code_{i + 1}"
# # #     previous_col = f"diagnosis_code_{i}"

# # #     gap_count = (
# # #         df[current_col].notna() &
# # #         df[previous_col].isna()
# # #     ).sum()

# # #     print(
# # #         f"{current_col} is populated while "
# # #         f"{previous_col} is missing: {gap_count} rows"
# # #     )
# # # print(df.head())
# # # print()
# # # print(df.info())
# # # claim_counts = df.groupby("claim_id")["service_nbr"].nunique()

# # # print("Total unique claims:", df["claim_id"].nunique())

# # # print(
# # #     "Claims with more than one service_nbr:",
# # #     (claim_counts > 1).sum()
# # # )

# # # print(
# # #     "Maximum service_nbr values for one claim:",
# # #     claim_counts.max()
# # # )
# # # diagnosis_cols = [
# # #     "diagnosis_code_1",
# # #     "diagnosis_code_2",
# # #     "diagnosis_code_3",
# # #     "diagnosis_code_4",
# # #     "diagnosis_code_5",
# # #     "diagnosis_code_6",
# # #     "diagnosis_code_7",
# # #     "diagnosis_code_8"
# # # ]

# # # duplicate_diagnosis_count = (
# # #     df[diagnosis_cols]
# # #     .apply(lambda row: row.dropna().duplicated().any(), axis=1)
# # #     .sum()
# # # )

# # # print(
# # #     "Claims with a repeated diagnosis code:",
# # #     duplicate_diagnosis_count
# # # )
# # # # ---------------------------------------------------------
# # # # Investigation: Diagnosis normalization collisions
# # # # ---------------------------------------------------------

# # # diagnosis_cols = [
# # #     "diagnosis_code_1",
# # #     "diagnosis_code_2",
# # #     "diagnosis_code_3",
# # #     "diagnosis_code_4",
# # #     "diagnosis_code_5",
# # #     "diagnosis_code_6",
# # #     "diagnosis_code_7",
# # #     "diagnosis_code_8"
# # # ]

# # # # Put all diagnosis values into one column
# # # diagnosis_values = df[diagnosis_cols].melt(
# # #     value_name="raw_code"
# # # )

# # # # Remove missing diagnosis values
# # # diagnosis_values = diagnosis_values.dropna(subset=["raw_code"])

# # # # Make sure we are working with strings
# # # diagnosis_values["raw_code"] = diagnosis_values["raw_code"].astype(str)

# # # # Apply the assignment's normalization rule:
# # # # 1. Convert to uppercase
# # # # 2. Remove dots
# # # diagnosis_values["normalized_code"] = (
# # #     diagnosis_values["raw_code"]
# # #     .str.upper()
# # #     .str.replace(".", "", regex=False)
# # # )

# # # # Find normalized codes that came from MORE THAN ONE
# # # # distinct raw representation
# # # collision_groups = (
# # #     diagnosis_values
# # #     .groupby("normalized_code")["raw_code"]
# # #     .nunique()
# # # )

# # # collision_codes = collision_groups[collision_groups > 1]

# # # print("\n========== NORMALIZATION COLLISION ANALYSIS ==========")

# # # print(
# # #     "Total distinct raw diagnosis codes:",
# # #     diagnosis_values["raw_code"].nunique()
# # # )

# # # print(
# # #     "Total distinct normalized diagnosis codes:",
# # #     diagnosis_values["normalized_code"].nunique()
# # # )

# # # print(
# # #     "Number of normalized codes with collisions:",
# # #     len(collision_codes)
# # # )

# # # # Show the actual collisions
# # # if len(collision_codes) > 0:

# # #     collision_details = (
# # #         diagnosis_values[
# # #             diagnosis_values["normalized_code"].isin(collision_codes.index)
# # #         ]
# # #         [["raw_code", "normalized_code"]]
# # #         .drop_duplicates()
# # #         .sort_values(["normalized_code", "raw_code"])
# # #     )

# # #     print("\nActual normalization collisions:")
# # #     print(collision_details.to_string(index=False))

# # # else:
# # #     print("\nNo normalization collisions found.")
# # # print(df["service_from_date"].head(20).to_list())

# # # print("\nMinimum date value:")
# # # print(df["service_from_date"].min())

# # # print("\nMaximum date value:")
# # # print(df["service_from_date"].max())
# # # # =========================================================
# # # # SOURCE A - PATIENT DEMOGRAPHIC INVESTIGATION
# # # # =========================================================

# # # demographic_cols = [
# # #     "patient_birth_year",
# # #     "patient_gender",
# # #     "patient_zip3"
# # # ]

# # # print("\n========== PATIENT DEMOGRAPHICS ==========")

# # # # Missing values
# # # print("\n--- Missing values ---")
# # # print(df[demographic_cols].isna().sum())

# # # # Unique values / distributions
# # # print("\n--- Patient birth year ---")
# # # print("Unique values:", df["patient_birth_year"].nunique())
# # # print("Minimum:", df["patient_birth_year"].min())
# # # print("Maximum:", df["patient_birth_year"].max())

# # # print("\n--- Gender ---")
# # # print(df["patient_gender"].value_counts(dropna=False))

# # # print("\n--- ZIP3 ---")
# # # print("Unique ZIP3 values:", df["patient_zip3"].nunique())
# # # print("Minimum:", df["patient_zip3"].min())
# # # print("Maximum:", df["patient_zip3"].max())
# # # # ---------------------------------------------------------
# # # # Check whether demographic missingness matches
# # # # missing patient_id
# # # # ---------------------------------------------------------

# # # missing_patient = df["patient_id"].isna()

# # # demographic_missing = (
# # #     df["patient_birth_year"].isna()
# # #     & df["patient_gender"].isna()
# # #     & df["patient_zip3"].isna()
# # # )

# # # print("\n========== MISSING PATIENT / DEMOGRAPHIC CHECK ==========")

# # # print(
# # #     "Missing patient_id:",
# # #     missing_patient.sum()
# # # )

# # # print(
# # #     "Missing all demographic fields:",
# # #     demographic_missing.sum()
# # # )

# # # print(
# # #     "Missing patient_id AND all demographics:",
# # #     (missing_patient & demographic_missing).sum()
# # # )

# # # print(
# # #     "Demographics missing while patient_id exists:",
# # #     ((~missing_patient) & demographic_missing).sum()
# # # )
# # # # ---------------------------------------------------------
# # # # Approximate age at service date
# # # # ---------------------------------------------------------

# # # age_check = df[
# # #     ["patient_birth_year", "service_from_date"]
# # # ].dropna().copy()

# # # age_check["service_year"] = (
# # #     age_check["service_from_date"].astype(str).str[:4].astype(int)
# # # )

# # # age_check["approx_age"] = (
# # #     age_check["service_year"]
# # #     - age_check["patient_birth_year"].astype(int)
# # # )

# # # print("\n========== APPROXIMATE AGE CHECK ==========")

# # # print("Minimum approximate age:", age_check["approx_age"].min())
# # # print("Maximum approximate age:", age_check["approx_age"].max())

# # # print("\nAge distribution:")
# # # print(
# # #     age_check["approx_age"]
# # #     .value_counts()
# # #     .sort_index()
# # # )
# # # print("\n========== ZIP3 VALUES ==========")

# # # print(
# # #     sorted(
# # #         df["patient_zip3"]
# # #         .dropna()
# # #         .unique()
# # #     )
# # # )
# # # # =========================================================
# # # # SOURCE A - PROVIDER INVESTIGATION
# # # # =========================================================

# # # provider_cols = [
# # #     "provider_rendering_id",
# # #     "provider_referring_id",
# # #     "provider_billing_id"
# # # ]

# # # print("\n========== PROVIDER INVESTIGATION ==========")

# # # print("\n--- Missing values ---")
# # # print(df[provider_cols].isna().sum())

# # # for col in provider_cols:

# # #     print(f"\n--- {col} ---")

# # #     print("Unique values:", df[col].nunique(dropna=True))
# # #     print("Minimum:", df[col].min())
# # #     print("Maximum:", df[col].max())

# # #     print("Sample values:")
# # #     print(
# # #         df[col]
# # #         .dropna()
# # #         .drop_duplicates()
# # #         .head(20)
# # #         .tolist()
# # #     )
# # # # =========================================================
# # # # Provider ID format investigation
# # # # =========================================================

# # # print("\n========== PROVIDER ID FORMAT ==========")

# # # for col in provider_cols:

# # #     values = df[col].dropna().astype("int64").astype(str)

# # #     lengths = values.str.len().value_counts().sort_index()

# # #     print(f"\n--- {col} ---")
# # #     print("Digit-length distribution:")
# # #     print(lengths)
# # # # =========================================================
# # # # Provider role relationship
# # # # =========================================================

# # # print("\n========== PROVIDER ROLE RELATIONSHIPS ==========")

# # # rendering_billing_same = (
# # #     df["provider_rendering_id"]
# # #     == df["provider_billing_id"]
# # # )

# # # print(
# # #     "Rendering provider = Billing provider:",
# # #     rendering_billing_same.sum()
# # # )

# # # print(
# # #     "Rendering provider != Billing provider:",
# # #     (~rendering_billing_same).sum()
# # # )

# # # referring_present = df["provider_referring_id"].notna()

# # # rendering_referring_same = (
# # #     df["provider_rendering_id"]
# # #     == df["provider_referring_id"]
# # # )

# # # billing_referring_same = (
# # #     df["provider_billing_id"]
# # #     == df["provider_referring_id"]
# # # )

# # # print(
# # #     "Rows with referring provider:",
# # #     referring_present.sum()
# # # )

# # # print(
# # #     "Rendering = Referring among non-null referring:",
# # #     rendering_referring_same[referring_present].sum()
# # # )

# # # print(
# # #     "Billing = Referring among non-null referring:",
# # #     billing_referring_same[referring_present].sum()
# # # )
# # # # =========================================================
# # # # SOURCE A - FINANCIAL FIELD INVESTIGATION
# # # # =========================================================

# # # financial_cols = [
# # #     "unit_of_svc_amt",
# # #     "bill_amt"
# # # ]

# # # print("\n========== FINANCIAL INVESTIGATION ==========")

# # # for col in financial_cols:

# # #     print(f"\n--- {col} ---")

# # #     print("Missing:", df[col].isna().sum())
# # #     print("Unique values:", df[col].nunique())
# # #     print("Minimum:", df[col].min())
# # #     print("Maximum:", df[col].max())

# # #     print("Zero values:", (df[col] == 0).sum())
# # #     print("Negative values:", (df[col] < 0).sum())

# # #     print("Sample values:")
# # #     print(
# # #         df[col]
# # #         .drop_duplicates()
# # #         .head(20)
# # #         .tolist()
# # #     )
# # # print("\n========== FINANCIAL RELATIONSHIP ==========")

# # # print(
# # #     "Rows where unit_of_svc_amt > bill_amt:",
# # #     (df["unit_of_svc_amt"] > df["bill_amt"]).sum()
# # # )

# # # print(
# # #     "Rows where unit_of_svc_amt == bill_amt:",
# # #     (df["unit_of_svc_amt"] == df["bill_amt"]).sum()
# # # )

# # # print(
# # #     "Rows where unit_of_svc_amt < bill_amt:",
# # #     (df["unit_of_svc_amt"] < df["bill_amt"]).sum()
# # # )
# # # # =========================================================
# # # # SOURCE A - SERVICE NUMBER / FINANCIAL RELATIONSHIP
# # # # =========================================================

# # # print("\n========== SERVICE / AMOUNT RELATIONSHIP ==========")

# # # print(
# # #     "Unique service_nbr values:",
# # #     df["service_nbr"].nunique()
# # # )

# # # print(
# # #     "Minimum service_nbr:",
# # #     df["service_nbr"].min()
# # # )

# # # print(
# # #     "Maximum service_nbr:",
# # #     df["service_nbr"].max()
# # # )

# # # print("\nSample service_nbr values:")
# # # print(
# # #     sorted(df["service_nbr"].unique())[:30]
# # # )
# # # print("\n========== SERVICE NUMBER DISTRIBUTION ==========")

# # # print(
# # #     df["service_nbr"]
# # #     .value_counts()
# # #     .sort_index()
# # # )
# # # # =========================================================
# # # # SOURCE A - SERVICE / FACILITY / CLAIM TYPE INVESTIGATION
# # # # =========================================================

# # # service_type_cols = [
# # #     "place_of_svc_cd",
# # #     "facility_type_cd",
# # #     "claim_type_cd"
# # # ]

# # # print("\n========== SERVICE / FACILITY / CLAIM TYPE ==========")

# # # for col in service_type_cols:

# # #     print(f"\n--- {col} ---")

# # #     print("Data type:", df[col].dtype)
# # #     print("Missing:", df[col].isna().sum())
# # #     print("Unique values:", df[col].nunique())

# # #     print("Value counts:")
# # #     print(
# # #         df[col]
# # #         .value_counts(dropna=False)
# # #         .sort_index()
# # #     )
# # # # =========================================================
# # # # SOURCE A - RELATIONSHIP BETWEEN CLAIM TYPE AND POS
# # # # =========================================================

# # # print("\n========== CLAIM TYPE vs PLACE OF SERVICE ==========")

# # # claim_pos = pd.crosstab(
# # #     df["claim_type_cd"],
# # #     df["place_of_svc_cd"]
# # # )

# # # print(claim_pos)
# # # print("\n========== FACILITY TYPE vs PLACE OF SERVICE ==========")

# # # facility_pos = pd.crosstab(
# # #     df["facility_type_cd"],
# # #     df["place_of_svc_cd"]
# # # )

# # # print(facility_pos)
# # # print("\n========== CLAIM TYPE vs FACILITY TYPE ==========")

# # # claim_facility = pd.crosstab(
# # #     df["claim_type_cd"],
# # #     df["facility_type_cd"]
# # # )

# # # print(claim_facility)
# # # # =========================================================
# # # # SOURCE A - PLAN / SOURCE INVESTIGATION
# # # # =========================================================

# # # plan_source_cols = [
# # #     "primary_plan_id",
# # #     "secondary_plan_id",
# # #     "data_source"
# # # ]

# # # print("\n========== PLAN / SOURCE INVESTIGATION ==========")

# # # for col in plan_source_cols:

# # #     print(f"\n--- {col} ---")

# # #     print("Data type:", df[col].dtype)
# # #     print("Missing:", df[col].isna().sum())
# # #     print("Unique values:", df[col].nunique(dropna=True))

# # #     print("Value counts:")
# # #     print(
# # #         df[col]
# # #         .value_counts(dropna=False)
# # #         .head(30)
# # #     )
# # # # =========================================================
# # # # DIAGNOSIS DICTIONARY INVESTIGATION
# # # # =========================================================

# # # DX_FILE_PATH = "data/raw/dx_dictionary.csv.xlsx"

# # # print("\n========== DIAGNOSIS DICTIONARY ==========")

# # # dx = pd.read_excel(DX_FILE_PATH)

# # # print("\nShape:")
# # # print(dx.shape)

# # # print("\nColumns:")
# # # print(dx.columns.tolist())

# # # print("\nData types:")
# # # print(dx.dtypes)

# # # print("\nMissing values:")
# # # print(dx.isna().sum())

# # # print("\nSample:")
# # # print(dx.head(20).to_string(index=False))

# # # print("\nUnique values:")
# # # for col in dx.columns:
# # #     print(
# # #         col,
# # #         "→",
# # #         dx[col].nunique(dropna=True)
# # #     )

# # # print("\n========== DIAGNOSIS DICTIONARY COVERAGE ==========")

# # # diagnosis_cols = [
# # #     "diagnosis_code_1",
# # #     "diagnosis_code_2",
# # #     "diagnosis_code_3",
# # #     "diagnosis_code_4",
# # #     "diagnosis_code_5",
# # #     "diagnosis_code_6",
# # #     "diagnosis_code_7",
# # #     "diagnosis_code_8",
# # # ]

# # # source_diagnosis = df[diagnosis_cols].melt(
# # #     value_name="diagnosis_code"
# # # )["diagnosis_code"]

# # # source_diagnosis = source_diagnosis.dropna()

# # # source_diagnosis = (
# # #     source_diagnosis
# # #     .astype(str)
# # #     .str.upper()
# # #     .str.replace(".", "", regex=False)
# # # )

# # # source_codes = set(source_diagnosis.unique())

# # # dictionary_codes = set(
# # #     dx["dx_code"]
# # #     .astype(str)
# # #     .str.upper()
# # #     .str.replace(".", "", regex=False)
# # #     .unique()
# # # )

# # # missing_from_dictionary = sorted(
# # #     source_codes - dictionary_codes
# # # )

# # # unused_dictionary_codes = sorted(
# # #     dictionary_codes - source_codes
# # # )

# # # print("Distinct Source A diagnosis codes:", len(source_codes))
# # # print("Distinct dictionary diagnosis codes:", len(dictionary_codes))
# # # print(
# # #     "Source A codes missing from dictionary:",
# # #     len(missing_from_dictionary)
# # # )
# # # print(
# # #     "Dictionary codes not used by Source A:",
# # #     len(unused_dictionary_codes)
# # # )

# # # print("\nMissing from dictionary:")
# # # print(missing_from_dictionary)

# # # print("\nDictionary codes not used by Source A:")
# # # print(unused_dictionary_codes)


# # # print("\n========== DICTIONARY KEY CHECK ==========")

# # # dictionary_key_counts = (
# # #     dx.groupby("dx_code")
# # #       .size()
# # #       .reset_index(name="count")
# # # )

# # # duplicate_dictionary_keys = dictionary_key_counts[
# # #     dictionary_key_counts["count"] > 1
# # # ]

# # # print(
# # #     "Duplicate dx_code groups:",
# # #     len(duplicate_dictionary_keys)
# # # )
# # # print("\n========== MISSING DICTIONARY CODE FREQUENCY ==========")

# # # missing_code_frequency = (
# # #     source_diagnosis[
# # #         source_diagnosis.isin(missing_from_dictionary)
# # #     ]
# # #     .value_counts()
# # #     .rename_axis("diagnosis_code")
# # #     .reset_index(name="row_count")
# # # )

# # # print(
# # #     missing_code_frequency
# # #     .to_string(index=False)
# # # )
# # # print("\n========== MISSING CODES BY DIAGNOSIS POSITION ==========")

# # # for col in diagnosis_cols:

# # #     count = (
# # #         df[col]
# # #         .astype(str)
# # #         .str.upper()
# # #         .str.replace(".", "", regex=False)
# # #         .isin(missing_from_dictionary)
# # #         .sum()
# # #     )

# # #     if count > 0:
# # #         print(col, "→", count)
# # # print("\n========== MISSING CODE DISTRIBUTION ==========")

# # # missing_code_rows = source_diagnosis[
# # #     source_diagnosis.isin(missing_from_dictionary)
# # # ]

# # # print(
# # #     missing_code_rows.value_counts()
# # #     .sort_index()
# # # )
# # # print("\n========== MISSING CODE COMBINATIONS ==========")

# # # for code in missing_from_dictionary:

# # #     print(f"\n--- {code} ---")

# # #     mask = df[diagnosis_cols].apply(
# # #         lambda col: (
# # #             col.astype(str)
# # #             .str.upper()
# # #             .str.replace(".", "", regex=False)
# # #             == code
# # #         )
# # #     ).any(axis=1)

# # #     subset = df.loc[
# # #         mask,
# # #         ["claim_id", "patient_id"] + diagnosis_cols
# # #     ]

# # #     print("Claims containing code:", len(subset))

# # #     print(
# # #         subset.head(10).to_string(index=False)
# # #     )
# # #=====================Source B====================================================================================================
# # print("\n========== SOURCE B ENCOUNTER / LINE INVESTIGATION ==========")
# # source_b = pd.read_excel("data/raw/source_b_claims.csv.xlsx")

# # print("\n--- Encounter ID ---")
# # print("Total rows:", len(source_b))
# # print("Unique encounter IDs:", source_b["encounter_id"].nunique())

# # encounter_counts = source_b.groupby("encounter_id").size()

# # print("Encounters with more than one row:",
# #       (encounter_counts > 1).sum())

# # print("Maximum rows for one encounter:",
# #       encounter_counts.max())

# # print("\n--- Line number ---")
# # print("Unique line_nbr values:", source_b["line_nbr"].nunique())
# # print("Minimum line_nbr:", source_b["line_nbr"].min())
# # print("Maximum line_nbr:", source_b["line_nbr"].max())

# # print("\n--- Encounter + line grain ---")
# # print(
# #     "Duplicate encounter_id + line_nbr combinations:",
# #     source_b.duplicated(
# #         subset=["encounter_id", "line_nbr"]
# #     ).sum()
# # )

# # print("\n--- Encounter + diagnosis ---")

# # duplicate_mask = source_b.duplicated(
# #     subset=["encounter_id", "dx_code"],
# #     keep=False
# # )

# # duplicate_rows = source_b[duplicate_mask].copy()

# # print(
# #     "Rows involved in duplicate encounter + diagnosis:",
# #     len(duplicate_rows)
# # )

# # print(
# #     "Unique duplicated encounter + diagnosis combinations:",
# #     duplicate_rows[
# #         ["encounter_id", "dx_code"]
# #     ].drop_duplicates().shape[0]
# # )

# # print("\nExamples:")
# # print(
# #     duplicate_rows[
# #         [
# #             "encounter_id",
# #             "line_nbr",
# #             "dx_code",
# #             "svc_date",
# #             "svc_amount",
# #             "billed_amount"
# #         ]
# #     ]
# #     .head(20)
# #     .to_string(index=False)
# # )
# # print("\n========== SOURCE B DIAGNOSIS INVESTIGATION ==========")

# # dx = source_b["dx_code"].astype(str)

# # print("\n--- Missing diagnosis codes ---")
# # print("Missing:", source_b["dx_code"].isna().sum())

# # print("\n--- Raw diagnosis codes ---")
# # print("Distinct codes:", source_b["dx_code"].nunique())
# # print("Codes containing dots:", dx.str.contains(r"\.", regex=True).sum())
# # print("Codes containing lowercase:", dx.str.contains(r"[a-z]", regex=True).sum())
# # print("Codes with leading/trailing spaces:",
# #       (dx != dx.str.strip()).sum())

# # print("\nSample diagnosis codes:")
# # print(source_b["dx_code"].drop_duplicates().head(50).to_list())

# # # Normalize only for investigation — DO NOT modify source_b yet
# # normalized_dx = (
# #     dx
# #     .str.strip()
# #     .str.upper()
# #     .str.replace(".", "", regex=False)
# # )

# # print("\n--- Normalization collision check ---")

# # collision_check = pd.DataFrame({
# #     "raw_code": dx,
# #     "normalized_code": normalized_dx
# # }).drop_duplicates()

# # collision_groups = (
# #     collision_check
# #     .groupby("normalized_code")["raw_code"]
# #     .nunique()
# # )

# # collisions = collision_groups[collision_groups > 1]

# # print("Distinct raw diagnosis codes:",
# #       dx.nunique())

# # print("Distinct normalized diagnosis codes:",
# #       normalized_dx.nunique())

# # print("Normalized codes with collisions:",
# #       len(collisions))

# # if len(collisions) > 0:
# #     print("\nCollision examples:")
# #     print(
# #         collision_check[
# #             collision_check["normalized_code"].isin(collisions.index)
# #         ]
# #         .sort_values("normalized_code")
# #         .head(50)
# #         .to_string(index=False)
# #     )
# # print("\n========== SOURCE B SERVICE DATE INVESTIGATION ==========")

# # START_DATE = pd.Timestamp("2018-01-01")
# # END_DATE = pd.Timestamp("2025-02-28")

# # print("\n--- Service date ---")
# # print("Data type:", source_b["svc_date"].dtype)
# # print("Missing:", source_b["svc_date"].isna().sum())
# # print("Minimum date:", source_b["svc_date"].min())
# # print("Maximum date:", source_b["svc_date"].max())

# # out_of_range = (
# #     (source_b["svc_date"] < START_DATE)
# #     | (source_b["svc_date"] > END_DATE)
# # )

# # print("\n--- Required date range ---")
# # print("Allowed range:", START_DATE.date(), "to", END_DATE.date())
# # print("Rows within range:", (~out_of_range).sum())
# # print("Rows outside range:", out_of_range.sum())

# # if out_of_range.sum() > 0:
# #     print("\nOut-of-range date examples:")
# #     print(
# #         source_b.loc[
# #             out_of_range,
# #             ["encounter_id", "line_nbr", "svc_date", "dx_code"]
# #         ]
# #         .head(20)
# #         .to_string(index=False)
# #     )
# # print("\n========== SOURCE B BIRTH YEAR INVESTIGATION ==========")

# # valid_dates = source_b[
# #     (source_b["svc_date"] >= START_DATE)
# #     & (source_b["svc_date"] <= END_DATE)
# # ].copy()

# # print("\n--- Birth year ---")
# # print("Rows after date filter:", len(valid_dates))
# # print("Missing:", valid_dates["birth_yr"].isna().sum())
# # print("Unique birth years:", valid_dates["birth_yr"].nunique())
# # print("Minimum birth year:", valid_dates["birth_yr"].min())
# # print("Maximum birth year:", valid_dates["birth_yr"].max())

# # print("\nBirth year distribution:")
# # print(valid_dates["birth_yr"].value_counts().sort_index().head(20))
# # print("\n========== SOURCE B GENDER INVESTIGATION ==========")

# # print("\n--- Gender ---")
# # print("Missing:", valid_dates["gender"].isna().sum())
# # print("Unique values:", valid_dates["gender"].nunique())

# # print("\nGender value counts:")
# # print(valid_dates["gender"].value_counts().sort_index())
# # print("\n========== SOURCE B ZIP3 INVESTIGATION ==========")

# # print("\n--- ZIP3 ---")
# # print("Missing:", valid_dates["zip3"].isna().sum())
# # print("Unique values:", valid_dates["zip3"].nunique())
# # print("Minimum:", valid_dates["zip3"].min())
# # print("Maximum:", valid_dates["zip3"].max())

# # print("\nZIP3 values:")
# # print(sorted(valid_dates["zip3"].unique()))
# # print("\n========== SOURCE B PLACE OF SERVICE INVESTIGATION ==========")

# # print("\n--- pos_code ---")
# # print("Missing:", valid_dates["pos_code"].isna().sum())
# # print("Unique values:", valid_dates["pos_code"].nunique())

# # print("\nValue counts:")
# # print(valid_dates["pos_code"].value_counts().sort_index())
# # print("\n========== SOURCE B FACILITY TYPE INVESTIGATION ==========")

# # print("\n--- fclty_cd ---")
# # print("Missing:", valid_dates["fclty_cd"].isna().sum())
# # print("Unique values:", valid_dates["fclty_cd"].nunique())

# # print("\nValue counts:")
# # print(valid_dates["fclty_cd"].value_counts().sort_index())
# # print("\n========== SOURCE B CLAIM TYPE INVESTIGATION ==========")

# # print("\n--- clm_typ ---")
# # print("Missing:", valid_dates["clm_typ"].isna().sum())
# # print("Unique values:", valid_dates["clm_typ"].nunique())

# # print("\nValue counts:")
# # print(valid_dates["clm_typ"].value_counts().sort_index())
# # print("\n========== SOURCE B RENDERING NPI INVESTIGATION ==========")

# # print("\n--- rendering_npi ---")
# # print("Missing:", valid_dates["rendering_npi"].isna().sum())
# # print("Unique values:", valid_dates["rendering_npi"].nunique())

# # print("\nDigit-length distribution:")
# # print(
# #     valid_dates["rendering_npi"]
# #     .astype(str)
# #     .str.len()
# #     .value_counts()
# #     .sort_index()
# # )
# # print("\n========== SOURCE B REFERRING NPI INVESTIGATION ==========")

# # print("\n--- referring_npi ---")
# # print("Missing:", valid_dates["referring_npi"].isna().sum())
# # print("Non-missing:", valid_dates["referring_npi"].notna().sum())
# # print("Unique non-missing values:",
# #       valid_dates["referring_npi"].dropna().nunique())

# # print("\nDigit-length distribution:")
# # print(
# #     valid_dates["referring_npi"]
# #     .dropna()
# #     .astype(str)
# #     .str.replace(r"\.0$", "", regex=True)
# #     .str.len()
# #     .value_counts()
# #     .sort_index()
# # )
# # print("\n========== SOURCE B BILLING NPI INVESTIGATION ==========")

# # print("\n--- billing_npi ---")
# # print("Missing:", valid_dates["billing_npi"].isna().sum())
# # print("Unique values:", valid_dates["billing_npi"].nunique())

# # print("\nDigit-length distribution:")
# # print(
# #     valid_dates["billing_npi"]
# #     .astype(str)
# #     .str.len()
# #     .value_counts()
# #     .sort_index()
# # )
# # print("\n========== SOURCE B PRIMARY PLAN INVESTIGATION ==========")

# # print("\n--- payer_primary ---")
# # print("Missing:", valid_dates["payer_primary"].isna().sum())
# # print("Unique values:", valid_dates["payer_primary"].nunique())

# # print("\nSample values:")
# # print(valid_dates["payer_primary"].drop_duplicates().head(30).to_list())

# # print("\nTop values:")
# # print(valid_dates["payer_primary"].value_counts().head(20))
# # print("\n========== SOURCE B SECONDARY PLAN INVESTIGATION ==========")

# # print("\n--- payer_secondary ---")
# # print("Missing:", valid_dates["payer_secondary"].isna().sum())
# # print("Non-missing:", valid_dates["payer_secondary"].notna().sum())
# # print("Unique non-missing values:",
# #       valid_dates["payer_secondary"].dropna().nunique())

# # print("\nSample values:")
# # print(
# #     valid_dates["payer_secondary"]
# #     .dropna()
# #     .drop_duplicates()
# #     .head(30)
# #     .to_list()
# # )

# # print("\nTop values:")
# # print(
# #     valid_dates["payer_secondary"]
# #     .value_counts()
# #     .head(20)
# # )
# # print("\n========== SOURCE B FINANCIAL INVESTIGATION ==========")

# # for col in ["svc_amount", "billed_amount"]:

# #     print(f"\n--- {col} ---")
# #     print("Missing:", valid_dates[col].isna().sum())
# #     print("Unique values:", valid_dates[col].nunique())
# #     print("Minimum:", valid_dates[col].min())
# #     print("Maximum:", valid_dates[col].max())
# #     print("Zero values:", (valid_dates[col] == 0).sum())
# #     print("Negative values:", (valid_dates[col] < 0).sum())

# # print("\n========== FINANCIAL RELATIONSHIP ==========")

# # print(
# #     "svc_amount > billed_amount:",
# #     (valid_dates["svc_amount"] > valid_dates["billed_amount"]).sum()
# # )

# # print(
# #     "svc_amount == billed_amount:",
# #     (valid_dates["svc_amount"] == valid_dates["billed_amount"]).sum()
# # )

# # print(
# #     "svc_amount < billed_amount:",
# #     (valid_dates["svc_amount"] < valid_dates["billed_amount"]).sum()
# # )
# # print("\n========== SOURCE B SOURCE IDENTIFIER ==========")

# # print("Missing:", valid_dates["src"].isna().sum())
# # print("Unique values:", valid_dates["src"].nunique())

# # print("\nValue counts:")
# # print(valid_dates["src"].value_counts())
# # print("\n========== SOURCE B MEMBER INVESTIGATION ==========")

# # print("\n--- member_id ---")
# # print("Missing:", valid_dates["member_id"].isna().sum())
# # print("Unique members:", valid_dates["member_id"].nunique())

# # print("\nMember ID length distribution:")
# # print(
# #     valid_dates["member_id"]
# #     .astype(str)
# #     .str.len()
# #     .value_counts()
# #     .sort_index()
# # )

# # print("\nSample member IDs:")
# # print(
# #     valid_dates["member_id"]
# #     .drop_duplicates()
# #     .head(20)
# #     .to_list()
# # )

# # print("\n--- Member / Encounter relationship ---")

# # encounters_per_member = (
# #     valid_dates
# #     .groupby("member_id")["encounter_id"]
# #     .nunique()
# # )

# # print(
# #     "Members with more than one encounter:",
# #     (encounters_per_member > 1).sum()
# # )

# # print(
# #     "Maximum encounters for one member:",
# #     encounters_per_member.max()
# # )

# # members_per_encounter = (
# #     valid_dates
# #     .groupby("encounter_id")["member_id"]
# #     .nunique()
# # )

# # print(
# #     "Encounters with more than one member:",
# #     (members_per_encounter > 1).sum()
# # )

# # print(
# #     "Maximum members for one encounter:",
# #     members_per_encounter.max()
# # )
# # print("\n========== SOURCE B SECONDARY PLAN FINAL CHECK ==========")

# # print("Missing:", valid_dates["payer_secondary"].isna().sum())
# # print("Non-missing:", valid_dates["payer_secondary"].notna().sum())
# # print("Unique non-missing:",
# #       valid_dates["payer_secondary"].dropna().nunique())
# print("\n========== SOURCE C ID / GRAIN INVESTIGATION ==========")
# df = pd.read_excel("data/raw/source_c_claims.csv.xlsx")


# print("\n--- pt_ref ---")
# print("Missing:", df["pt_ref"].isna().sum())
# print("Unique:", df["pt_ref"].nunique())

# print("\npt_ref length distribution:")
# print(
#     df["pt_ref"]
#     .astype(str)
#     .str.len()
#     .value_counts()
#     .sort_index()
# )

# print("\n--- claim_ref ---")
# print("Missing:", df["claim_ref"].isna().sum())
# print("Unique:", df["claim_ref"].nunique())

# print("\nclaim_ref length distribution:")
# print(
#     df["claim_ref"]
#     .astype(str)
#     .str.len()
#     .value_counts()
#     .sort_index()
# )

# print("\n--- version ---")
# print("Missing:", df["version"].isna().sum())
# print("Unique:", df["version"].nunique())
# print("Values:")
# print(df["version"].value_counts().sort_index())

# print("\n--- seq ---")
# print("Missing:", df["seq"].isna().sum())
# print("Unique:", df["seq"].nunique())
# print("Minimum:", df["seq"].min())
# print("Maximum:", df["seq"].max())

# print("\n--- claim_ref + seq grain ---")
# print(
#     "Duplicate claim_ref + seq:",
#     df.duplicated(
#         subset=["claim_ref", "seq"],
#         keep=False
#     ).sum()
# )

# print("\n--- claim_ref + diagnosis_codes ---")
# print(
#     "Duplicate claim_ref + diagnosis_codes:",
#     df.duplicated(
#         subset=["claim_ref", "diagnosis_codes"],
#         keep=False
#     ).sum()
# )

# print("\n--- claim_ref + version + seq ---")
# print(
#     "Duplicate claim_ref + version + seq:",
#     df.duplicated(
#         subset=["claim_ref", "version", "seq"],
#         keep=False
#     ).sum()
# )
# print("\n========== SOURCE C DUPLICATE INVESTIGATION ==========")

# duplicate_mask = df.duplicated(
#     subset=["claim_ref", "diagnosis_codes"],
#     keep=False
# )

# duplicate_examples = (
#     df[duplicate_mask]
#     .sort_values(["claim_ref", "diagnosis_codes"])
# )

# print(
#     duplicate_examples.to_string(index=False)
# )
# print("\n========== SOURCE C VERSION INVESTIGATION ==========")

# print("\n--- Claim + version ---")
# print(
#     "Unique claim + version combinations:",
#     df[["claim_ref", "version"]].drop_duplicates().shape[0]
# )

# print(
#     "Duplicate claim + version:",
#     df.duplicated(
#         subset=["claim_ref", "version"],
#         keep=False
#     ).sum()
# )

# print("\n--- Claims by number of versions ---")

# versions_per_claim = (
#     df.groupby("claim_ref")["version"]
#     .nunique()
# )

# print(
#     "Claims with 1 version:",
#     (versions_per_claim == 1).sum()
# )

# print(
#     "Claims with >1 version:",
#     (versions_per_claim > 1).sum()
# )

# print(
#     "Maximum versions for one claim:",
#     versions_per_claim.max()
# )

# print("\nVersion combinations:")
# print(
#     df.groupby("claim_ref")["version"]
#     .unique()
#     .value_counts()
# )
# print("\n========== SOURCE C VERSION SEQUENCE CHECK ==========")

# version_sequences = (
#     df.groupby("claim_ref")["version"]
#     .apply(lambda x: sorted(x.unique()))
# )

# print("\nVersion sequence distribution:")
# print(version_sequences.value_counts())

# print("\nClaims with non-sequential versions:")

# non_sequential = version_sequences[
#     version_sequences.apply(
#         lambda x: x != list(range(1, len(x) + 1))
#     )
# ]

# print("Count:", len(non_sequential))

# if len(non_sequential) > 0:
#     print(non_sequential.head(20))
# print("\n========== SOURCE C DIAGNOSIS EXPANSION INVESTIGATION ==========")

# source_c_dx = df.copy()

# # Create version-aware claim ID
# source_c_dx["claim_id_temp"] = (
#     source_c_dx["claim_ref"].astype(str)
#     + "_V"
#     + source_c_dx["version"].astype(str)
# )

# # Split pipe-separated diagnoses into separate rows
# source_c_dx["diagnosis_code"] = (
#     source_c_dx["diagnosis_codes"]
#     .astype(str)
#     .str.split("|")
# )

# source_c_dx = source_c_dx.explode(
#     "diagnosis_code"
# ).copy()

# print("Rows after diagnosis expansion:", len(source_c_dx))

# # Normalize diagnosis codes
# source_c_dx["diagnosis_code"] = (
#     source_c_dx["diagnosis_code"]
#     .astype(str)
#     .str.strip()
#     .str.upper()
#     .str.replace(".", "", regex=False)
# )

# print("\nDistinct normalized diagnosis codes:")
# print(source_c_dx["diagnosis_code"].nunique())

# # Final grain duplicate check
# duplicate_mask = source_c_dx.duplicated(
#     subset=["claim_id_temp", "diagnosis_code"],
#     keep=False
# )

# duplicate_rows = source_c_dx[duplicate_mask]

# print("\n========== FINAL GRAIN DUPLICATE CHECK ==========")

# print(
#     "Rows involved in duplicate claim + diagnosis:",
#     len(duplicate_rows)
# )

# print(
#     "Unique duplicated claim + diagnosis combinations:",
#     duplicate_rows[
#         ["claim_id_temp", "diagnosis_code"]
#     ].drop_duplicates().shape[0]
# )

# print("\nDuplicate examples:")

# print(
#     duplicate_rows[
#         [
#             "claim_ref",
#             "version",
#             "claim_id_temp",
#             "diagnosis_codes",
#             "diagnosis_code"
#         ]
#     ]
#     .head(30)
#     .to_string(index=False)
# )
# print("\n========== SOURCE C DIAGNOSIS EXPANSION ==========")

# source_c_dx = df.copy()

# # Create version-aware claim ID
# source_c_dx["claim_id"] = (
#     source_c_dx["claim_ref"].astype(str)
#     + "_V"
#     + source_c_dx["version"].astype(str)
# )

# # Split multiple diagnoses and create one row per diagnosis
# source_c_dx["diagnosis_code"] = (
#     source_c_dx["diagnosis_codes"]
#     .astype(str)
#     .str.split("|")
# )

# source_c_dx = source_c_dx.explode(
#     "diagnosis_code"
# ).copy()

# # Normalize diagnosis code
# source_c_dx["diagnosis_code"] = (
#     source_c_dx["diagnosis_code"]
#     .astype(str)
#     .str.strip()
#     .str.upper()
#     .str.replace(".", "", regex=False)
# )

# print("Rows after diagnosis expansion:", len(source_c_dx))
# print(
#     "Unique CLAIM_ID:",
#     source_c_dx["claim_id"].nunique()
# )
# print(
#     "Unique diagnosis codes:",
#     source_c_dx["diagnosis_code"].nunique()
# )

# # Final grain check
# duplicate_mask = source_c_dx.duplicated(
#     subset=["claim_id", "diagnosis_code"],
#     keep=False
# )

# print("\n========== FINAL GRAIN CHECK ==========")
# print(
#     "Duplicate CLAIM_ID + DIAGNOSIS_CODE:",
#     duplicate_mask.sum()
# )

# if duplicate_mask.sum() > 0:
#     print(
#         source_c_dx.loc[
#             duplicate_mask,
#             ["claim_id", "diagnosis_code"]
#         ].drop_duplicates()
#     )
# else:
#     print("Grain check passed: no duplicates.")
# print("\n========== SOURCE C SERVICE DATE INVESTIGATION ==========")

# print("\n--- Service date ---")
# print("Data type:", df["date_of_service"].dtype)
# print("Missing:", df["date_of_service"].isna().sum())
# print("Minimum date:", df["date_of_service"].min())
# print("Maximum date:", df["date_of_service"].max())

# START_DATE = pd.Timestamp("2018-01-01")
# END_DATE = pd.Timestamp("2025-02-28")

# within_range = (
#     (df["date_of_service"] >= START_DATE)
#     & (df["date_of_service"] <= END_DATE)
# )

# print("\n--- Required date range ---")
# print("Allowed range:", START_DATE.date(), "to", END_DATE.date())
# print("Rows within range:", within_range.sum())
# print("Rows outside range:", (~within_range).sum())

# print("\nOut-of-range date examples:")
# print(
#     df.loc[
#         ~within_range,
#         ["claim_ref", "version", "seq", "date_of_service", "diagnosis_codes"]
#     ]
#     .head(20)
#     .to_string(index=False)
# )
# print("\n========== SOURCE C DATE CHECK AFTER DIAGNOSIS EXPANSION ==========")

# START_DATE = pd.Timestamp("2018-01-01")
# END_DATE = pd.Timestamp("2025-02-28")

# date_valid = (
#     (source_c_dx["date_of_service"] >= START_DATE)
#     & (source_c_dx["date_of_service"] <= END_DATE)
# )

# print("Diagnosis-level rows after expansion:", len(source_c_dx))
# print("Rows within date range:", date_valid.sum())
# print("Rows outside date range:", (~date_valid).sum())

# print("\nOut-of-range diagnosis-level examples:")
# print(
#     source_c_dx.loc[
#         ~date_valid,
#         [
#             "claim_ref",
#             "version",
#             "claim_id",
#             "date_of_service",
#             "diagnosis_code"
#         ]
#     ]
#     .head(20)
#     .to_string(index=False)
# )
# print("\n========== SOURCE C BIRTH YEAR INVESTIGATION ==========")

# START_DATE = pd.Timestamp("2018-01-01")
# END_DATE = pd.Timestamp("2025-02-28")

# valid_date_dx = source_c_dx[
#     (source_c_dx["date_of_service"] >= START_DATE)
#     & (source_c_dx["date_of_service"] <= END_DATE)
# ].copy()

# print("Diagnosis-level rows after date filter:", len(valid_date_dx))

# print("\n--- Birth year ---")
# print("Data type:", valid_date_dx["yob"].dtype)
# print("Missing:", valid_date_dx["yob"].isna().sum())
# print("Unique birth years:", valid_date_dx["yob"].nunique())
# print("Minimum birth year:", valid_date_dx["yob"].min())
# print("Maximum birth year:", valid_date_dx["yob"].max())

# print("\nBirth year distribution:")
# print(
#     valid_date_dx["yob"]
#     .value_counts()
#     .sort_index()
# )
# print("\n========== SOURCE C GENDER INVESTIGATION ==========")

# print("--- sex ---")
# print("Data type:", valid_date_dx["sex"].dtype)
# print("Missing:", valid_date_dx["sex"].isna().sum())
# print("Unique values:", valid_date_dx["sex"].nunique())

# print("\nGender value counts:")
# print(valid_date_dx["sex"].value_counts(dropna=False))
# print("\n========== SOURCE C ZIP3 INVESTIGATION ==========")

# print("--- zip_3 ---")
# print("Data type:", valid_date_dx["zip_3"].dtype)
# print("Missing:", valid_date_dx["zip_3"].isna().sum())
# print("Unique values:", valid_date_dx["zip_3"].nunique())
# print("Minimum:", valid_date_dx["zip_3"].min())
# print("Maximum:", valid_date_dx["zip_3"].max())

# print("\nZIP3 values:")
# print(sorted(valid_date_dx["zip_3"].dropna().unique()))
# print("\n========== SOURCE C PLACE OF SERVICE INVESTIGATION ==========")

# print("--- service_place ---")
# print("Data type:", valid_date_dx["service_place"].dtype)
# print("Missing:", valid_date_dx["service_place"].isna().sum())
# print("Unique values:", valid_date_dx["service_place"].nunique())

# print("\nValue counts:")
# print(valid_date_dx["service_place"].value_counts().sort_index())
# print("\n========== SOURCE C FACILITY INVESTIGATION ==========")

# print("--- facility ---")
# print("Data type:", valid_date_dx["facility"].dtype)
# print("Missing:", valid_date_dx["facility"].isna().sum())
# print("Unique values:", valid_date_dx["facility"].nunique())

# print("\nValue counts:")
# print(valid_date_dx["facility"].value_counts().sort_index())
# print("\n========== SOURCE C CLAIM CATEGORY INVESTIGATION ==========")

# print("--- claim_category ---")
# print("Data type:", valid_date_dx["claim_category"].dtype)
# print("Missing:", valid_date_dx["claim_category"].isna().sum())
# print("Unique values:", valid_date_dx["claim_category"].nunique())

# print("\nValue counts:")
# print(valid_date_dx["claim_category"].value_counts().sort_index())
# print("\n========== SOURCE C RENDERING NPI INVESTIGATION ==========")

# print("--- npi_rendering ---")
# print("Data type:", valid_date_dx["npi_rendering"].dtype)
# print("Missing:", valid_date_dx["npi_rendering"].isna().sum())
# print("Unique values:", valid_date_dx["npi_rendering"].nunique())

# print("\nDigit-length distribution:")
# print(
#     valid_date_dx["npi_rendering"]
#     .astype(str)
#     .str.len()
#     .value_counts()
#     .sort_index()
# )
# print("\n========== SOURCE C REFERRING NPI INVESTIGATION ==========")

# print("--- npi_referring ---")
# print("Data type:", valid_date_dx["npi_referring"].dtype)
# print("Missing:", valid_date_dx["npi_referring"].isna().sum())
# print("Non-missing:", valid_date_dx["npi_referring"].notna().sum())
# print(
#     "Unique non-missing values:",
#     valid_date_dx["npi_referring"].dropna().nunique()
# )

# print("\nDigit-length distribution:")
# print(
#     valid_date_dx["npi_referring"]
#     .dropna()
#     .astype(int)
#     .astype(str)
#     .str.len()
#     .value_counts()
#     .sort_index()
# )
# print("\n========== SOURCE C BILLING NPI INVESTIGATION ==========")

# print("--- npi_billing ---")
# print("Data type:", valid_date_dx["npi_billing"].dtype)
# print("Missing:", valid_date_dx["npi_billing"].isna().sum())
# print("Unique values:", valid_date_dx["npi_billing"].nunique())

# print("\nDigit-length distribution:")
# print(
#     valid_date_dx["npi_billing"]
#     .astype(str)
#     .str.len()
#     .value_counts()
#     .sort_index()
# )
# print("\n========== SOURCE C PRIMARY PLAN INVESTIGATION ==========")

# print("--- plan_1 ---")
# print("Data type:", valid_date_dx["plan_1"].dtype)
# print("Missing:", valid_date_dx["plan_1"].isna().sum())
# print("Unique values:", valid_date_dx["plan_1"].nunique())

# print("\nSample values:")
# print(valid_date_dx["plan_1"].dropna().head(20).tolist())

# print("\nTop values:")
# print(valid_date_dx["plan_1"].value_counts().head(20))
# print("\n========== SOURCE C SECONDARY PLAN INVESTIGATION ==========")

# print("--- plan_2 ---")
# print("Data type:", valid_date_dx["plan_2"].dtype)
# print("Missing:", valid_date_dx["plan_2"].isna().sum())
# print("Non-missing:", valid_date_dx["plan_2"].notna().sum())
# print(
#     "Unique non-missing:",
#     valid_date_dx["plan_2"].dropna().nunique()
# )

# print("\nSample values:")
# print(valid_date_dx["plan_2"].dropna().head(20).tolist())

# print("\nTop values:")
# print(valid_date_dx["plan_2"].value_counts().head(20))
# print("\n========== SOURCE C FINANCIAL INVESTIGATION ==========")

# print("\n--- amount_unit ---")
# print("Data type:", valid_date_dx["amount_unit"].dtype)
# print("Missing:", valid_date_dx["amount_unit"].isna().sum())
# print("Unique values:", valid_date_dx["amount_unit"].nunique())
# print("Minimum:", valid_date_dx["amount_unit"].min())
# print("Maximum:", valid_date_dx["amount_unit"].max())
# print("Zero values:", (valid_date_dx["amount_unit"] == 0).sum())
# print("Negative values:", (valid_date_dx["amount_unit"] < 0).sum())

# print("\n--- amount_billed ---")
# print("Data type:", valid_date_dx["amount_billed"].dtype)
# print("Missing:", valid_date_dx["amount_billed"].isna().sum())
# print("Unique values:", valid_date_dx["amount_billed"].nunique())
# print("Minimum:", valid_date_dx["amount_billed"].min())
# print("Maximum:", valid_date_dx["amount_billed"].max())
# print("Zero values:", (valid_date_dx["amount_billed"] == 0).sum())
# print("Negative values:", (valid_date_dx["amount_billed"] < 0).sum())
# print("\n========== SOURCE C FINANCIAL RELATIONSHIP ==========")

# print(
#     "amount_unit > amount_billed:",
#     (valid_date_dx["amount_unit"] > valid_date_dx["amount_billed"]).sum()
# )

# print(
#     "amount_unit == amount_billed:",
#     (valid_date_dx["amount_unit"] == valid_date_dx["amount_billed"]).sum()
# )

# print(
#     "amount_unit < amount_billed:",
#     (valid_date_dx["amount_unit"] < valid_date_dx["amount_billed"]).sum()
# )
# print("\n========== SOURCE C SOURCE IDENTIFIER ==========")

# print("--- source_system ---")
# print("Data type:", valid_date_dx["source_system"].dtype)
# print("Missing:", valid_date_dx["source_system"].isna().sum())
# print("Unique values:", valid_date_dx["source_system"].nunique())

# print("\nValue counts:")
# print(valid_date_dx["source_system"].value_counts())
# source_a = pd.read_csv("data/processed/source_a_final.csv")
# source_b = pd.read_csv("data/processed/source_b_final.csv")
# source_c = pd.read_csv("data/processed/source_c_final.csv")
# print("\n========== CROSS-SOURCE SCHEMA CHECK ==========")

# print("\nSource A columns:")
# print(source_a.columns.tolist())

# print("\nSource B columns:")
# print(source_b.columns.tolist())

# print("\nSource C columns:")
# print(source_c.columns.tolist())

# print("\nA == B columns:",
#       source_a.columns.tolist() == source_b.columns.tolist())

# print("B == C columns:",
#       source_b.columns.tolist() == source_c.columns.tolist())

# print("A == C columns:",
#       source_a.columns.tolist() == source_c.columns.tolist())
# print("\n========== COLUMN-BY-COLUMN SCHEMA ==========")

# for i, column in enumerate(source_a.columns, start=1):
#     print(
#         i,
#         column,
#         "| A:", column in source_a.columns,
#         "| B:", column in source_b.columns,
#         "| C:", column in source_c.columns
#     )
# print("\n========== SOURCE ROW COUNTS ==========")

# print("Source A:", len(source_a))
# print("Source B:", len(source_b))
# print("Source C:", len(source_c))

# print("Expected combined rows:",
#       len(source_a) + len(source_b) + len(source_c))
# print("\n========== SRC VALIDATION ==========")

# print("Source A:")
# print(source_a["SRC"].value_counts())

# print("\nSource B:")
# print(source_b["SRC"].value_counts())

# print("\nSource C:")
# print(source_c["SRC"].value_counts())
# print("\n========== CROSS-SOURCE GRAIN CHECK ==========")

# for name, data in [
#     ("SOURCE A", source_a),
#     ("SOURCE B", source_b),
#     ("SOURCE C", source_c)
# ]:
#     duplicates = data.duplicated(
#         subset=["CLAIM_ID", "DIAGNOSIS_CODE"],
#         keep=False
#     ).sum()

#     print(
#         name,
#         "duplicate CLAIM_ID + DIAGNOSIS_CODE:",
#         duplicates
#     )
# COMMON_COLUMNS = [
#     "SRC",
#     "PATIENT_ID",
#     "BIRTH_YEAR",
#     "GENDER",
#     "ZIP3",
#     "CLAIM_ID",
#     "SERVICE_DATE",
#     "DIAGNOSIS_CODE",
#     "PLACE_OF_SERVICE",
#     "RENDERING_NPI",
#     "REFERRING_NPI",
#     "BILLING_NPI",
#     "PRIMARY_PLAN_ID",
#     "BILLED_AMOUNT"
# ]
# print("\n========== CROSS-SOURCE DATA TYPE CHECK ==========")

# for column in COMMON_COLUMNS:
#     print(
#         f"{column:<20} | "
#         f"A: {source_a[column].dtype} | "
#         f"B: {source_b[column].dtype} | "
#         f"C: {source_c[column].dtype}"
#     )
#     print("\n========== CROSS-SOURCE MISSING VALUE CHECK ==========")

# for column in COMMON_COLUMNS:
#     print(
#         f"{column:<20} | "
#         f"A: {source_a[column].isna().sum():>6} | "
#         f"B: {source_b[column].isna().sum():>6} | "
#         f"C: {source_c[column].isna().sum():>6}"
#     )
# print("\n========== CROSS-SOURCE RULE VALIDATION ==========")

# for name, df in [
#     ("SOURCE A", source_a),
#     ("SOURCE B", source_b),
#     ("SOURCE C", source_c)
# ]:
#     print(f"\n--- {name} ---")

#     print(
#         "Invalid gender:",
#         (~df["GENDER"].isin(["M", "F"])).sum()
#     )

#     print(
#         "Diagnosis codes with dots:",
#         df["DIAGNOSIS_CODE"]
#         .str.contains(".", regex=False, na=False)
#         .sum()
#     )

#     print(
#         "Diagnosis codes with lowercase:",
#         df["DIAGNOSIS_CODE"]
#         .str.contains(r"[a-z]", regex=True, na=False)
#         .sum()
#     )

#     print(
#         "Invalid SRC:",
#         (~df["SRC"].isin(["SRC_A", "SRC_B", "SRC_C"])).sum()
#     )

#     service_dates = pd.to_datetime(
#         df["SERVICE_DATE"],
#         errors="raise"
#     )

#     print(
#         "Invalid service dates:",
#         (
#             (service_dates < "2018-01-01")
#             | (service_dates > "2025-02-28")
#         ).sum()
#     )
# dictionary = pd.read_excel(
#     "data/raw/dx_dictionary.csv.xlsx"
# )

# print("\n========== DIAGNOSIS DICTIONARY INVESTIGATION ==========")

# print("Rows:", len(dictionary))
# print("Columns:", len(dictionary.columns))

# print("\nColumns:")
# print(dictionary.columns.tolist())

# print("\nTop 10 rows:")
# print(dictionary.head(10).to_string(index=False))

# print("\nData types:")
# print(dictionary.dtypes)

# print("\nMissing values:")
# print(dictionary.isna().sum())
# print("\n========== DICTIONARY DX CODE CHECK ==========")

# print("Unique dx_code:", dictionary["dx_code"].nunique())

# print(
#     "Codes containing dots:",
#     dictionary["dx_code"]
#     .str.contains(".", regex=False, na=False)
#     .sum()
# )

# print(
#     "Codes containing lowercase:",
#     dictionary["dx_code"]
#     .str.contains(r"[a-z]", regex=True, na=False)
#     .sum()
# )

# print(
#     "Codes with leading/trailing spaces:",
#     (
#         dictionary["dx_code"]
#         != dictionary["dx_code"].str.strip()
#     ).sum()
# )

# print("\nAll dictionary codes:")
# print(
#     dictionary["dx_code"]
#     .sort_values()
#     .tolist()
# )
# print("\n========== DICTIONARY GRAIN CHECK ==========")

# duplicate_mask = dictionary.duplicated(
#     subset=["dx_code"],
#     keep=False
# )

# print(
#     "Rows involved in duplicate dx_code:",
#     duplicate_mask.sum()
# )

# print(
#     "Unique duplicated dx_code combinations:",
#     dictionary.loc[
#         duplicate_mask,
#         "dx_code"
#     ].nunique()
# )

# if duplicate_mask.any():
#     print("\nDuplicate examples:")
#     print(
#         dictionary.loc[duplicate_mask]
#         .sort_values("dx_code")
#         .to_string(index=False)
#     )
# combined = pd.read_csv(
#     "data/processed/combined_claims.csv"
# )

# dictionary = pd.read_excel(
#     "data/raw/dx_dictionary.csv.xlsx"
# )
# print("\n========== COMBINED DATASET LOADED ==========")
# print("Rows:", len(combined))
# print("Columns:", len(combined.columns))
# print("Unique diagnosis codes:",
#       combined["DIAGNOSIS_CODE"].nunique())
# print("\n========== DICTIONARY COVERAGE CHECK ==========")

# claim_codes = set(
#     combined["DIAGNOSIS_CODE"]
#     .dropna()
#     .unique()
# )

# dictionary_codes = set(
#     dictionary["dx_code"]
#     .dropna()
#     .unique()
# )

# matched_codes = claim_codes & dictionary_codes
# unmatched_codes = claim_codes - dictionary_codes

# print("Unique claim diagnosis codes:", len(claim_codes))
# print("Dictionary diagnosis codes:", len(dictionary_codes))
# print("Matched diagnosis codes:", len(matched_codes))
# print("Unmatched diagnosis codes:", len(unmatched_codes))

# print("\nUnmatched diagnosis codes:")
# print(sorted(unmatched_codes))
# print("\n========== UNMATCHED CLAIM ROWS ==========")

# unmatched_rows = combined[
#     ~combined["DIAGNOSIS_CODE"].isin(dictionary_codes)
# ]

# print("Rows with unmatched diagnosis codes:", len(unmatched_rows))

# print("\nUnmatched code row counts:")
# print(
#     unmatched_rows["DIAGNOSIS_CODE"]
#     .value_counts()
#     .sort_index()
# )
# print("\n========== DICTIONARY VERSION CHECK ==========")

# print("ICD versions:")
# print(dictionary["icd_version"].value_counts())

# print("\n========== DICTIONARY DESCRIPTION CHECK ==========")

# print(
#     "Empty descriptions:",
#     (
#         dictionary["dx_description"]
#         .astype(str)
#         .str.strip()
#         .eq("")
#     ).sum()
# )

# print(
#     "Unique descriptions:",
#     dictionary["dx_description"].nunique()
# )

# print("\n========== CLAIM / DICTIONARY CODE COMPARISON ==========")

# print("Claim codes not in dictionary:")
# print(
#     sorted(
#         set(combined["DIAGNOSIS_CODE"].unique())
#         - set(dictionary["dx_code"].unique())
#     )
# )

# print("\nDictionary codes not present in claims:")
# print(
#     sorted(
#         set(dictionary["dx_code"].unique())
#         - set(combined["DIAGNOSIS_CODE"].unique())
#     )
# )
# print("\n========== ENDPOINT INVESTIGATION ==========")

# print(
#     "Total rows:",
#     len(combined)
# )

# print(
#     "Distinct claims:",
#     combined["CLAIM_ID"].nunique()
# )

# print(
#     "Distinct patients:",
#     combined["PATIENT_ID"].nunique()
# )

# print(
#     "Distinct diagnosis codes:",
#     combined["DIAGNOSIS_CODE"].nunique()
# )
# print("\n========== CROSS-SOURCE CLAIM OVERLAP ==========")

# claim_source_counts = (
#     combined
#     .groupby("CLAIM_ID")["SRC"]
#     .nunique()
# )

# print(
#     "Claims appearing in exactly 1 source:",
#     (claim_source_counts == 1).sum()
# )

# print(
#     "Claims appearing in multiple sources:",
#     (claim_source_counts > 1).sum()
# )

# print(
#     "Maximum sources for one claim:",
#     claim_source_counts.max()
# )
# print("\n========== CLAIM ID DISTRIBUTION BY SOURCE ==========")

# print(
#     combined.groupby("SRC")["CLAIM_ID"]
#     .nunique()
# )
# print("\n========== SOURCE C VERSION / CLAIM ID INVESTIGATION ==========")

# source_c_combined = combined[
#     combined["SRC"] == "SRC_C"
# ].copy()

# # Remove the version suffix we created:
# # C0001366_V1 -> C0001366
# source_c_combined["BASE_CLAIM_ID"] = (
#     source_c_combined["CLAIM_ID"]
#     .str.replace(r"_V[123]$", "", regex=True)
# )

# print(
#     "Source C current distinct CLAIM_ID:",
#     source_c_combined["CLAIM_ID"].nunique()
# )

# print(
#     "Source C distinct base claim_ref:",
#     source_c_combined["BASE_CLAIM_ID"].nunique()
# )

# print(
#     "Expected Source C claims:",
#     68205 - 25101 - 23516
# )
# print("\n========== SOURCE C BASE CLAIM + DIAGNOSIS CHECK ==========")

# duplicate_mask = source_c_combined.duplicated(
#     subset=[
#         "BASE_CLAIM_ID",
#         "DIAGNOSIS_CODE"
#     ],
#     keep=False
# )

# print(
#     "Rows involved in duplicate "
#     "BASE_CLAIM_ID + DIAGNOSIS_CODE:",
#     duplicate_mask.sum()
# )

# print(
#     "Unique duplicated "
#     "BASE_CLAIM_ID + DIAGNOSIS_CODE:",
#     source_c_combined.loc[
#         duplicate_mask,
#         ["BASE_CLAIM_ID", "DIAGNOSIS_CODE"]
#     ].drop_duplicates().shape[0]
# )

# print(
#     "Rows after deduplicating "
#     "BASE_CLAIM_ID + DIAGNOSIS_CODE:",
#     len(
#         source_c_combined.drop_duplicates(
#             subset=[
#                 "BASE_CLAIM_ID",
#                 "DIAGNOSIS_CODE"
#             ]
#         )
#     )
# )


# print("\n========== SOURCE C VERSION INVESTIGATION ==========")

# # Extract version from the CLAIM_ID we created
# source_c["VERSION"] = (
#     source_c["CLAIM_ID"]
#     .str.extract(r"_V(\d+)$")[0]
#     .astype(int)
# )

# print("\nVersion row counts:")
# print(
#     source_c["VERSION"]
#     .value_counts()
#     .sort_index()
# )

# print("\nDiagnosis rows by version:")
# print(
#     source_c
#     .groupby("VERSION")
#     .size()
#     .sort_index()
# )

# print("\nClaims by version:")
# print(
#     source_c
#     .groupby("VERSION")["CLAIM_ID"]
#     .nunique()
#     .sort_index()
# )
# print("\n========== SOURCE C VERSION RELATIONSHIP ==========")

# # Get base claim_ref from the versioned CLAIM_ID
# source_c["BASE_CLAIM_ID"] = (
#     source_c["CLAIM_ID"]
#     .str.replace(r"_V[123]$", "", regex=True)
# )

# # Claims that have each version
# claims_v1 = set(
#     source_c.loc[
#         source_c["VERSION"] == 1,
#         "BASE_CLAIM_ID"
#     ]
# )

# claims_v2 = set(
#     source_c.loc[
#         source_c["VERSION"] == 2,
#         "BASE_CLAIM_ID"
#     ]
# )

# claims_v3 = set(
#     source_c.loc[
#         source_c["VERSION"] == 3,
#         "BASE_CLAIM_ID"
#     ]
# )

# print("Claims with V1:", len(claims_v1))
# print("Claims with V2:", len(claims_v2))
# print("Claims with V3:", len(claims_v3))

# print("\nV2 claims also having V1:")
# print(len(claims_v1 & claims_v2))

# print("V3 claims also having V1:")
# print(len(claims_v1 & claims_v3))

# print("V3 claims also having V2:")
# print(len(claims_v2 & claims_v3))

# print("V3 claims having V1 and V2:")
# print(len(claims_v1 & claims_v2 & claims_v3))
# print("\n========== V1 ROWS FOR V3 CLAIMS ==========")

# v3_claims = claims_v3

# v1_rows_for_v3_claims = source_c[
#     (source_c["VERSION"] == 1)
#     & (source_c["BASE_CLAIM_ID"].isin(v3_claims))
# ]

# print(
#     "V1 rows belonging to V3 claims:",
#     len(v1_rows_for_v3_claims)
# )

# print(
#     "V3 rows:",
#     len(
#         source_c[
#             source_c["VERSION"] == 3
#         ]
#     )
# )
# print("\n========== THREE-VERSION CLAIM DIAGNOSIS ROWS ==========")

# three_version_claims = (
#     claims_v1
#     & claims_v2
#     & claims_v3
# )

# three_version_rows = source_c[
#     source_c["BASE_CLAIM_ID"].isin(three_version_claims)
# ]

# print(
#     three_version_rows
#     .groupby("VERSION")
#     .size()
#     .sort_index()
# )

# print("\nUnique claim + diagnosis combinations by version:")

# print(
#     three_version_rows
#     .groupby("VERSION")
#     .apply(
#         lambda x: x[
#             ["BASE_CLAIM_ID", "DIAGNOSIS_CODE"]
#         ].drop_duplicates().shape[0]
#     )
# )
# print("\n========== VERSION DIAGNOSIS SET COMPARISON ==========")

# three_version_claims = (
#     claims_v1
#     & claims_v2
#     & claims_v3
# )

# three_version_data = source_c[
#     source_c["BASE_CLAIM_ID"].isin(three_version_claims)
# ].copy()

# diagnosis_sets = (
#     three_version_data
#     .groupby(
#         ["BASE_CLAIM_ID", "VERSION"]
#     )["DIAGNOSIS_CODE"]
#     .apply(set)
#     .unstack()
# )

# print("Three-version claims:", len(diagnosis_sets))

# print("\nDiagnosis sets identical V1 vs V2:")
# print(
#     (
#         diagnosis_sets[1]
#         == diagnosis_sets[2]
#     ).sum()
# )

# print("\nDiagnosis sets identical V2 vs V3:")
# print(
#     (
#         diagnosis_sets[2]
#         == diagnosis_sets[3]
#     ).sum()
# )

# print("\nDiagnosis sets identical V1 vs V3:")
# print(
#     (
#         diagnosis_sets[1]
#         == diagnosis_sets[3]
#     ).sum()
# )
# print("\n========== VERSION DIAGNOSIS COUNT DISTRIBUTION ==========")

# print(
#     three_version_data
#     .groupby(
#         ["BASE_CLAIM_ID", "VERSION"]
#     )["DIAGNOSIS_CODE"]
#     .nunique()
#     .groupby("VERSION")
#     .describe()
# )
# print("\n========== SOURCE C LATEST VERSION TEST ==========")

# latest_version = (
#     source_c
#     .groupby("BASE_CLAIM_ID")["VERSION"]
#     .transform("max")
# )

# latest_source_c = source_c[
#     source_c["VERSION"] == latest_version
# ].copy()

# print(
#     "Rows keeping latest version:",
#     len(latest_source_c)
# )

# print(
#     "Distinct claims keeping latest version:",
#     latest_source_c["BASE_CLAIM_ID"].nunique()
# )

# print(
#     "Rows expected:",
#     39354
# )

# print(
#     "Claims expected:",
#     19588
# )
import pandas as pd


FINAL_PATH = "data/processed/final_harmonized_claims.csv"

final_data = pd.read_csv(FINAL_PATH)


print("\n========== FINAL ENDPOINT VALIDATION ==========")


# =========================================================
# 1. Total rows
# =========================================================

print("\n1. Total rows in final output")
print("Actual:", len(final_data))
print("Expected:", 159704)
print("PASS" if len(final_data) == 159704 else "FAIL")


# =========================================================
# 2. Distinct claims
# =========================================================

distinct_claims = final_data["CLAIM_ID"].nunique()

print("\n2. Distinct claims across all sources")
print("Actual:", distinct_claims)
print("Expected:", 68205)
print("PASS" if distinct_claims == 68205 else "FAIL")


# =========================================================
# 3. Distinct patients
# =========================================================

distinct_patients = final_data["PATIENT_ID"].nunique()

print("\n3. Distinct patients")
print("Actual:", distinct_patients)
print("Expected:", 11963)
print("PASS" if distinct_patients == 11963 else "FAIL")


# =========================================================
# 4. Distinct diagnosis codes
# =========================================================

distinct_diagnoses = final_data["DIAGNOSIS_CODE"].nunique()

print("\n4. Distinct diagnosis codes")
print("Actual:", distinct_diagnoses)
print("Expected:", 44)
print("PASS" if distinct_diagnoses == 44 else "FAIL")


# =========================================================
# 5. Patient P00042 - distinct diagnosis codes
# =========================================================

patient_42 = final_data[
    final_data["PATIENT_ID"] == "P00042"
]

patient_42_diagnoses = patient_42[
    "DIAGNOSIS_CODE"
].nunique()

print("\n5. Patient P00042 - distinct diagnosis codes")
print("Actual:", patient_42_diagnoses)
print("Expected:", 7)
print("PASS" if patient_42_diagnoses == 7 else "FAIL")


# =========================================================
# 6. Patient P00042 - total rows
# =========================================================

patient_42_rows = len(patient_42)

print("\n6. Patient P00042 - total rows")
print("Actual:", patient_42_rows)
print("Expected:", 7)
print("PASS" if patient_42_rows == 7 else "FAIL")


# =========================================================
# 7. Diagnosis code format
# =========================================================

has_dots = (
    final_data["DIAGNOSIS_CODE"]
    .astype(str)
    .str.contains(".", regex=False)
    .any()
)

has_lowercase = (
    final_data["DIAGNOSIS_CODE"]
    .astype(str)
    .str.contains(
        r"[a-z]",
        regex=True
    )
    .any()
)

check_7 = not has_dots and not has_lowercase

print("\n7. No DIAGNOSIS_CODE contains a dot; all uppercase")
print("Contains dots:", has_dots)
print("Contains lowercase:", has_lowercase)
print("Expected: True")
print("PASS" if check_7 else "FAIL")


# =========================================================
# 8. SERVICE_DATE range
# =========================================================

final_data["SERVICE_DATE"] = pd.to_datetime(
    final_data["SERVICE_DATE"],
    errors="coerce"
)

invalid_dates = (
    final_data["SERVICE_DATE"].isna()
    |
    (final_data["SERVICE_DATE"] < pd.Timestamp("2018-01-01"))
    |
    (final_data["SERVICE_DATE"] > pd.Timestamp("2025-02-28"))
)

invalid_date_count = invalid_dates.sum()

print("\n8. All SERVICE_DATE between 2018-01-01 and 2025-02-28")
print("Invalid dates:", invalid_date_count)
print("Expected: 0 invalid dates")
print("PASS" if invalid_date_count == 0 else "FAIL")


# =========================================================
# 9. Empty PATIENT_ID
# =========================================================

empty_patient = (
    final_data["PATIENT_ID"].isna()
    |
    final_data["PATIENT_ID"]
    .astype(str)
    .str.strip()
    .eq("")
)

empty_patient_count = empty_patient.sum()

print("\n9. No row has an empty PATIENT_ID")
print("Empty PATIENT_ID rows:", empty_patient_count)
print("Expected: 0")
print("PASS" if empty_patient_count == 0 else "FAIL")


# =========================================================
# Additional grain check
# =========================================================

duplicate_grain = final_data.duplicated(
    subset=[
        "SRC",
        "CLAIM_ID",
        "DIAGNOSIS_CODE"
    ],
    keep=False
).sum()

print("\n========== FINAL GRAIN CHECK ==========")
print(
    "Duplicate SRC + CLAIM_ID + DIAGNOSIS_CODE:",
    duplicate_grain
)

print(
    "PASS"
    if duplicate_grain == 0
    else "FAIL"
)


# =========================================================
# Summary
# =========================================================

print("\n========== FINAL SUMMARY ==========")

checks = {
    "Total rows": len(final_data) == 159704,
    "Distinct claims": distinct_claims == 68205,
    "Distinct patients": distinct_patients == 11963,
    "Distinct diagnosis codes": distinct_diagnoses == 44,
    "P00042 distinct diagnoses": patient_42_diagnoses == 7,
    "P00042 total rows": patient_42_rows == 7,
    "Diagnosis code format": check_7,
    "Service date range": invalid_date_count == 0,
    "Patient ID not empty": empty_patient_count == 0,
    "Final grain": duplicate_grain == 0,
}

for check_name, passed in checks.items():
    print(
        f"{check_name}:",
        "PASS" if passed else "FAIL"
    )

print(
    "\nAll checks pass:",
    all(checks.values())
)