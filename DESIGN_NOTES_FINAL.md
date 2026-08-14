# DESIGN NOTES – Claims Harmonization Pipeline

## 1. What I Built

I built a claims harmonization pipeline for three different claim sources: Source A, Source B, and Source C.

The main purpose is to take the three raw files, understand the differences between them, clean and transform each source separately, convert them to one common target structure, combine them, add diagnosis descriptions, and finally validate the result.

The overall flow is:

```text
Source A -> Source A processing Source B -> Source B processing  -> Common target schema -> Harmonization -> Final output
Source C -> Source C processing /
```

I also added a `StageTracker` so I can see what happened to the row count at every important step. For each stage I record rows in, rows out, the change, and the reason.

I then added a FastAPI backend and a simple web UI. The UI allows the complete pipeline to be run without manually running Source A, Source B, Source C, and Harmonization separately.

The final verified output is:

- 159,704 rows
- 68,205 distinct claims
- 11,963 distinct patients
- 44 distinct diagnosis codes
- 15 columns

The final validation contains 10 acceptance checks and all 10 pass.

---

## 2. How I Started

I first uploaded the raw files into VS Code.

Before writing the actual transformations, I checked my Python version, created a virtual environment, and activated it.

I then created an inspection file so that I could understand the data before changing it.

I did this because I did not want to assume that similarly named columns behaved the same way in all three sources.

For example, Source A has multiple diagnosis columns, Source B has one diagnosis column and line numbers, and Source C stores multiple diagnosis codes together and also contains claim versions.

So I first investigated the data and then decided the transformations.

---

## 3. The Most Important Rule: Final Grain

The most important thing I understood was the final grain.

The final data is diagnosis-level data, and the required grain is:

```text
SRC + CLAIM_ID + DIAGNOSIS_CODE
```

This means one claim can have multiple rows when it has multiple diagnosis codes.

For example:

```text
SRC_A | A10001 | R97.20
SRC_A | A10001 | Z1234
SRC_A | A10001 | E119
```

are three valid rows for one claim.

But if the same diagnosis occurs twice inside the same claim, I should not keep two identical target-grain rows.

Understanding this grain helped me decide how to handle Source A diagnosis duplicates, Source B line numbers, and Source C versions.

---

# 1. Source A Investigation

## 4.1 Initial profile

Source A initially contained:

| Property | Value |
|---|---:|
| Rows | 26,004 |
| Columns | 26 |
| Memory | approximately 5.2 MB |
| String columns | 15 |
| Integer columns | 6 |
| Float columns | 5 |

I then inspected every column.

## 4.2 Source A columns

### `patient_id`

This identifies the patient associated with the claim.

One patient can have multiple claims and therefore multiple rows.

There were 25,602 non-null values out of 26,004 rows.

So:

```text
26,004 - 25,602 = 402
```

There were 402 rows with a missing patient ID.

The assignment requires rows with missing patient identifiers to be removed, so I applied that rule.

### `claim_id`

This identifies the claim.

Vendor A claim IDs start with `A`.

It maps to:

```text
CLAIM_ID
```

### `service_nbr`

This was present in Source A but is not in the final target schema.

I investigated it instead of simply ignoring it.

There were:

- 26,004 unique claims
- 0 claims with more than one service number
- maximum service number per claim = 1

Therefore it did not create another level of detail that needed to be preserved.

### `service_from_date`

The Source A service date was stored as an integer.

I needed to convert it into the target `SERVICE_DATE` representation.

The required rule is:

```text
2018-01-01 <= SERVICE_DATE <= 2025-02-28
```

After removing the 402 rows with missing patient IDs:

```text
25,602
```

remained.

After the date filter:

```text
25,101
```

remained.

So 501 rows were outside the required date range.

---

# 2. Source A Diagnosis Columns

Source A has eight diagnosis columns:

```text
diagnosis_code_1
diagnosis_code_2
diagnosis_code_3
diagnosis_code_4
diagnosis_code_5
diagnosis_code_6
diagnosis_code_7
diagnosis_code_8
```

Diagnosis code 1 was 100% populated and the later diagnosis columns became progressively less populated.

I did not treat the nulls in diagnosis columns 2–8 as bad records.

They mean that the claim simply did not have another diagnosis in that slot.

The important transformation was to expand the diagnosis columns into diagnosis-level rows.

For example:

```text
CLAIM_ID | D1 | D2 | D3
A100     | X  | Y  | Z
```

becomes:

```text
CLAIM_ID | DIAGNOSIS_CODE
A100     | X
A100     | Y
A100     | Z
```

That is why the row count increases.

The final tracked transformation was:

```text
25,101
   |
   v
diagnosis expansion
   |
   v
200,808
```

---

# 3. Source A Empty Diagnosis Removal

After expansion, many rows represented empty diagnosis slots.

Those rows should not exist in the final diagnosis-level dataset.

So I removed rows without a diagnosis code.

The count changed:

```text
200,808 -> 68,993
```

Therefore:

```text
131,815
```

empty diagnosis rows were removed.

This is different from dropping a whole claim because a later diagnosis slot was empty. I only removed the empty diagnosis-level rows after expansion.

---

# 4. Source A Diagnosis Normalization

I normalized diagnosis codes by:

- trimming whitespace
- converting to uppercase
- removing dots

I also checked whether normalization would cause two different raw codes to become the same normalized code.

There were:

```text
0 normalization collisions
```

So normalization did not merge two different raw codes.

---

# 5. Source A Repeated Diagnosis Investigation

I found cases where the same diagnosis appears in more than one diagnosis slot.

For example:

```text
diagnosis_code_1 = R97.20
diagnosis_code_2 = R97.20
```

Initially, checking `D1 == D2` found:

```text
446 rows
```

I investigated this further.

There were:

```text
26,004 total claims
24,499 claims with no repeated diagnosis
1,505 claims with at least one repeated diagnosis
```

So repeated diagnoses were a real property of the data.

I also checked `service_nbr` and found that it did not explain the duplicates because every claim had only one service number.

---

# 6. Why I Deduplicated Source A Diagnoses

I also investigated the financial fields.

The billed amount is recorded at the claim level, not separately for each diagnosis slot.

So if the same diagnosis appears twice, I do not have a reliable basis for splitting the billed amount between those two occurrences.

The final target grain is:

```text
SRC + CLAIM_ID + DIAGNOSIS_CODE
```

It does not contain the diagnosis-slot number.

Therefore I decided to collapse repeated diagnosis codes within the same claim.

The final tracked change was:

```text
68,993 -> 67,531
```

So 1,462 repeated diagnosis rows were removed.

This was a deliberate grain decision rather than simply removing duplicates without understanding the data.

---

# 7. Source A Other Fields

`patient_birth_year` maps to `BIRTH_YEAR`.

`patient_gender` is already represented as `M` and `F`, so it maps directly to `GENDER`.

`patient_zip3` maps to `ZIP3`. I checked that it follows the expected three-digit representation.

`place_of_svc_cd` maps to `PLACE_OF_SERVICE`.

`facility_type_cd` is not part of the final target schema, so it is not carried into the final output.

`claim_type_cd` is also not part of the final target schema, so it is excluded.

The three provider fields map as follows:

```text
provider_rendering_id -> RENDERING_NPI
provider_referring_id -> REFERRING_NPI
provider_billing_id   -> BILLING_NPI
```

The rendering and billing provider fields were present. Referring provider values can be missing, and the assignment does not require those rows to be removed.

`primary_plan_id` maps to `PRIMARY_PLAN_ID`.

`secondary_plan_id` is not required by the target schema. It had many missing values, but that does not mean the claim is bad, so I excluded the field rather than dropping the rows.

`unit_of_svc_amt` is not part of the target schema.

`bill_amt` maps to `BILLED_AMOUNT`.

`data_source` maps to `SRC`.

---

# 8. Source A Final Flow

The final Source A flow is:

```text
Raw Source A
26,004
   |
   v
Remove missing patient IDs
25,602
   |
   v
Service date filter
25,101
   |
   v
Diagnosis expansion
200,808
   |
   v
Remove empty diagnoses
68,993
   |
   v
Diagnosis normalization
68,993
   |
   v
Deduplicate CLAIM_ID + DIAGNOSIS_CODE
67,531
   |
   v
Target schema mapping
67,531
```

Final Source A:

```text
67,531 rows
25,101 distinct claims
```

---

# 9. Source B Investigation

Source B has a different structure.

The important fields are:

| Source B column | Meaning / handling |
|---|---|
| `member_id` | Patient/member identifier |
| `encounter_id` | Claim/encounter identifier |
| `line_nbr` | Line number within an encounter |
| `svc_date` | Service date |
| `dx_code` | Diagnosis code |
| `birth_yr` | Birth year |
| `gender` | Gender |
| `zip3` | ZIP3 |
| `pos_code` | Place of service |
| `fclty_cd` | Facility type |
| `clm_typ` | Claim type |
| `rendering_npi` | Rendering provider |
| `referring_npi` | Referring provider |
| `billing_npi` | Billing provider |
| `payer_primary` | Primary plan |
| `payer_secondary` | Secondary plan |
| `svc_amount` | Service amount |
| `billed_amount` | Billed amount |
| `src` | Source |

---

# 10. Source B Claim and Line Investigation

I found that `encounter_id` can repeat with different `line_nbr` values.

So I checked:

```text
encounter_id + line_nbr
```

and found no duplicates.

I also checked:

```text
encounter_id + dx_code
```

and found no duplicates.

Because the required final grain is:

```text
SRC + CLAIM_ID + DIAGNOSIS_CODE
```

the line number does not need to be carried into the final output.

The line number does not add a separate diagnosis-level record that needs to be preserved.

---

# 11. Source B Diagnosis Investigation

Source B already has one diagnosis code per row, unlike Source A.

So there was no eight-column diagnosis expansion.

I checked:

- missing diagnosis codes
- distinct diagnosis codes
- dots
- lowercase values
- leading/trailing spaces
- normalization collisions

The results were:

```text
Missing dx_code: 0
Distinct diagnosis codes: 44
Dots: 0
Lowercase values: 0
Leading/trailing spaces: 0
Normalization collisions: 0
```

The same 44 diagnosis codes found in Source A were also present in Source B.

---

# 12. Source B Diagnosis Observation

During Source B investigation, I noticed that the claims data contains 44 distinct diagnosis codes while the diagnosis dictionary contains 40 codes.

The four codes that are not present in the dictionary are:

```text
Q998
R6889
T889
Z9989
```

I recorded this observation for the later harmonization step.

I did **not** join the diagnosis dictionary inside Source B.

The dictionary is a common enrichment step that is performed after Source A, Source B, and Source C have been combined.

---

# 13. Source B Service Date

Source B has no missing service dates.

The date range is:

```text
Minimum: 2016-01-04
Maximum: 2025-12-30
```

The required range is:

```text
2018-01-01 through 2025-02-28
```

The results were:

```text
Raw rows:                  53,891
Outside required range:     1,072
After date filter:          52,819
```

So:

```text
53,891 -> 52,819
```

---

# 14. Source B Patient and Gender

`member_id` had no missing values.

I treat it as the patient identifier:

```text
member_id -> PATIENT_ID
```

One member can have multiple encounters, while one encounter belongs to one member.

`birth_yr` has no missing values and maps directly to `BIRTH_YEAR`.

Source B gender contains numeric values:

```text
1
2
```

There are no missing values.

There was no source documentation available that explicitly confirmed the meaning.

For harmonization I assumed:

```text
1 -> M
2 -> F
```

I have documented this as an assumption because it should be verified with source metadata in a production system.

---

# 15. Source B Provider Fields

Rendering NPI:

```text
Missing: 0
Unique NPIs: 23,515
All valid-date rows have 10-digit identifiers
```

So:

```text
rendering_npi -> RENDERING_NPI
```

Referring NPI:

```text
Missing: 16,031
Non-missing: 36,788
```

The non-missing identifiers are 10 digits.

I retained rows with missing referring NPIs because there is no rule requiring their removal.

Billing NPI:

```text
Missing: 0
Unique values: 23,514
All valid-date rows have 10-digit identifiers
```

So:

```text
billing_npi -> BILLING_NPI
```

---

# 16. Source B Plans and Financial Fields

`payer_primary` was complete:

```text
Missing: 0
Unique plans: 8,319
```

It maps to:

```text
PRIMARY_PLAN_ID
```

The secondary plan field is not required by the target.

Both financial fields were complete and non-negative.

I found 1,811 rows where `svc_amount > billed_amount`.

I did not remove them because no acceptance rule says these records are invalid.

The target requires:

```text
billed_amount -> BILLED_AMOUNT
```

`svc_amount` is excluded because it is not part of the target schema.

---

# 17. Source B Final Flow

```text
Raw Source B
53,891
   |
   v
Service date filter
52,819
   |
   v
Diagnosis normalization
52,819
   |
   v
Grain validation
52,819
   |
   v
Target schema mapping
52,819
```

Final Source B:

```text
52,819 rows
23,516 distinct claims
```

---

# 18. Source C – Initial Investigation

After Source B, I moved to Source C.

At this point I did not yet know that the Source C version handling would become a problem.

I initially proceeded with:

```text
claim_ref + version
```

as the Source C `CLAIM_ID`.

This is important because it was the approach I actually used in the first complete version of the pipeline.

I did not initially decide to keep only the latest version.

I first processed Source C completely using `claim_ref + version` and only later went back to investigate the version field after the final acceptance numbers did not match.

---

# 19. Source C – ID and Grain Investigation

I started by inspecting the identifiers.

## `pt_ref`

```text
Missing: 0
Unique: 9,793
Length: 6
```

I used this as the patient identifier:

```text
pt_ref -> PATIENT_ID
```

## `claim_ref`

```text
Missing: 0
Unique: 20,001
Length: 8
```

## `version`

```text
Missing: 0
Unique: 3

Version 1: 20,001
Version 2: 3,525
Version 3: 660
```

## `seq`

```text
Missing: 0
Unique: 24,186
Minimum: 1
Maximum: 24,186
```

I checked:

```text
claim_ref + seq
```

and found:

```text
0 duplicates
```

I checked:

```text
claim_ref + version + seq
```

and found:

```text
0 duplicates
```

I also checked:

```text
claim_ref + diagnosis_codes
```

and found:

```text
6 duplicates
```

At this point, I proceeded with:

```text
CLAIM_ID = claim_ref + version
```

because this was my initial interpretation of the Source C claim identity.

---

# 20. Source C – Processing With `claim_ref + version`

I then continued with the rest of Source C using that claim ID.

I inspected the remaining columns and mapped them to the common target concepts.

The important areas I checked were:

- patient identifier
- claim identifier
- service date
- diagnosis codes
- birth year
- gender
- ZIP3
- place of service
- facility
- provider fields
- plan fields
- billed amount
- source

I did not stop the transformation at the version investigation.

I continued and completed the Source C processing first.

---

# 21. Source C – Diagnosis Expansion

Source C contains multiple diagnosis codes in its diagnosis field.

I expanded those values into diagnosis-level rows.

For example, conceptually:

```text
DX1|DX2|DX3
```

becomes:

```text
DX1
DX2
DX3
```

The initial Source C exploration showed:

```text
Raw Source C:              24,186
After diagnosis expansion: 48,580
Valid-date diagnosis rows: 47,613
Out-of-range rows:            967
```

I then normalized the diagnosis codes by:

- trimming spaces
- converting to uppercase
- removing dots

I continued the Source C transformation using:

```text
CLAIM_ID = claim_ref + version
```

This was the first complete Source C implementation.

---

# 22. Source C – Other Field Checks

I checked the remaining fields after the diagnosis transformation.

## Gender

After the date filter and diagnosis expansion:

```text
Missing: 0
Unique values: 2
Male: 23,821
Female: 23,792
```

The final representation was normalized to:

```text
M
F
```

## Place of Service

```text
Missing: 0
Unique values: 8

11
19
21
22
23
31
49
81
```

No unexpected values were observed.

## Facility

```text
Missing: 0
Unique values: 5

1
2
3
4
5
```

No unexpected values were observed.

I also checked the other Source C fields needed for the common target schema.

At this point, Source C had been processed using the initial:

```text
claim_ref + version
```

claim-ID approach.

---

# 23. First Complete Harmonization

Once Source A, Source B, and Source C were processed, I moved to harmonization.

The important point is that the three source transformations were completed first.

The flow was:

```text
Source A
   |
   v
Source A target schema

Source B
   |
   v
Source B target schema

Source C
   |
   v
Source C target schema
   |
   +-------------------+
                       |
                       v
                 Combine sources
                       |
                       v
             Common harmonized data
```

The final target grain remained:

```text
SRC + CLAIM_ID + DIAGNOSIS_CODE
```

---

# 24. Combining the Three Sources

The first complete source-level results were:

```text
Source A: 67,531 rows
Source B: 52,819 rows
Source C: 47,613 rows
```

I combined the three processed datasets into the common target structure.

I also checked the final columns and data types so that the sources could be combined consistently.

At this point I had one combined claims dataset.

---

# 25. Diagnosis Dictionary – Performed After Combining

Only after the three sources were combined did I perform the diagnosis dictionary join.

The dictionary contains:

```text
40 diagnosis codes
```

while the claims data contains:

```text
44 diagnosis codes
```

The four claim diagnosis codes not found in the dictionary are:

```text
Q998
R6889
T889
Z9989
```

I used a LEFT JOIN.

The reason was that the dictionary provides the diagnosis description. A missing dictionary entry should not delete the original claim record.

So the logic is:

```text
Combined claims
       |
       | LEFT JOIN
       v
Diagnosis dictionary
       |
       +--> Match -> DIAGNOSIS_DESC populated
       |
       +--> No match -> DIAGNOSIS_DESC = null
```

This preserves the claims even when a diagnosis description is unavailable.

---

# 26. First Acceptance Testing

After completing:

```text
Source A
Source B
Source C
   |
   v
Combine
   |
   v
Dictionary LEFT JOIN
```

I started checking the acceptance requirements.

I checked:

- total rows
- distinct claims
- distinct patients
- distinct diagnosis codes
- patient-specific checks
- diagnosis formatting
- service-date range
- patient ID completeness
- reproducibility

The important problem appeared in the final row count and distinct claim count.

The numbers did not match the expected acceptance numbers.

So I did not treat the project as finished.

I went back and started investigating where the difference came from.

---

# 27. The Row Count and Unique Claim Mismatch

The problem was that the final data looked structurally correct, but:

```text
total rows
```

and:

```text
distinct claims
```

were not the expected values.

This was especially important because the patient and diagnosis-level checks were much closer to the expected result.

That suggested that the issue was probably related to how claims were being represented rather than a completely broken transformation.

I therefore went back to the source-level grain investigation.

---

# 28. Going Back to Source C

Source C was the first place I investigated because I had already noticed that:

```text
claim_ref
```

can have multiple:

```text
version
```

values.

My initial implementation had created:

```text
CLAIM_ID = claim_ref + version
```

I therefore asked:

> Am I accidentally treating multiple versions of one underlying claim as different claims?

I investigated the relationship again.

---

# 29. Source C – Version Investigation After the Mismatch

I checked the distribution again:

```text
Version 1: 20,001
Version 2: 3,525
Version 3: 660
```

The raw Source C file has:

```text
24,186 rows
```

but only:

```text
20,001 unique claim_ref values
```

This showed that the extra records are related to multiple versions of the same underlying claim reference.

I then considered what happens if I use:

```text
claim_ref + version
```

as the final claim ID.

In that case:

```text
claim_ref = same
version = different
```

becomes:

```text
different CLAIM_IDs
```

That can increase the distinct claim count.

This explained why the claim count was not matching the acceptance expectation.

---

# 30. Source C – Investigating the Version Meaning

I then went back to the source structure rather than changing the code blindly.

I checked:

```text
claim_ref
version
seq
claim_ref + seq
claim_ref + version + seq
claim_ref + diagnosis_codes
```

The results were:

```text
claim_ref + seq duplicates: 0
claim_ref + version + seq duplicates: 0
claim_ref + diagnosis_codes duplicates: 6
```

The key observation was that `version` represents multiple versions of the same underlying `claim_ref`.

Therefore, treating:

```text
claim_ref + version
```

as separate final claims was not consistent with the expected final distinct-claim result.

This was the point where I changed my understanding of Source C.

---

# 31. Final Source C Version Decision

After the investigation, I changed the Source C handling so that the highest version for each `claim_ref` is retained.

So the final logic became:

```text
claim_ref
   |
   +-- version 1
   +-- version 2
   +-- version 3
           |
           v
      keep highest
```

The older versions are not treated as separate final claims.

The important part for me was that this was **not** the rule I used in my first implementation.

I first used:

```text
claim_ref + version
```

completed the pipeline, saw the acceptance mismatch, and then investigated the data to reach this final decision.

---

# 32. Why This Investigation Mattered

The complete debugging process was:

```text
Initial Source C decision
        |
        v
CLAIM_ID = claim_ref + version
        |
        v
Complete Source C
        |
        v
Combine Source A + B + C
        |
        v
LEFT JOIN dictionary
        |
        v
Run acceptance checks
        |
        v
Row count / claim count mismatch
        |
        v
Go back to Source C
        |
        v
Investigate claim_ref + version
        |
        v
Understand version relationship
        |
        v
Change version handling
        |
        v
Run again
        |
        v
Acceptance numbers match
```

This was one of the most important parts of the project.

---

# 33. Final Harmonization After the Investigation

After fixing the Source C version handling, the complete data flow became:

```text
Source A processing
        |
Source B processing
        |
Source C processing
        |
        v
Common target schema
        |
        v
Combine sources
        |
        v
LEFT JOIN diagnosis dictionary
        |
        v
Final harmonized dataset
        |
        v
Acceptance validation
```

The dictionary remained a common post-combination enrichment step.

---

# 34. Complete Pipeline

Once the source transformations and harmonization were correct, I created `pipeline.py`.

The purpose of this file is to run the complete workflow in one place.

It does:

```text
1. Create one StageTracker
2. Run Source A
3. Run Source B
4. Run Source C
5. Run Harmonization
6. Print final row count
7. Print final column count
8. Print all tracked stages
9. Return final data and tracker
```

A new user therefore does not need to manually run:

```text
source_a.py
source_b.py
source_c.py
harmonize.py
```

The pipeline calls the functions in the correct order.

---

# 35. StageTracker

I then added a `StageTracker`.

The reason was that I wanted to see exactly what happened to the row count at every stage.

For example:

```text
Stage:
Source A - Remove missing patient IDs

Rows in:
26,004

Rows out:
25,602

Change:
-402

Reason:
Missing patient IDs were removed
```

The tracker records:

- stage name
- rows in
- rows out
- change
- reason

I create one tracker:

```python
tracker = StageTracker()
```

and pass the same tracker to:

```text
run_source_a()
run_source_b()
run_source_c()
run_harmonization()
```

This gives me one complete stage history for the entire pipeline run.

---

# 36. Processed Output Directory

The source transformations save generated files under:

```text
data/processed/
```

I changed the project so that this directory is created automatically when needed.

Therefore, a new user does not need to manually create the processed folder.

The raw files are the inputs.

The processed files are generated outputs.

---

# 37. FastAPI

After the Python pipeline was working, I added FastAPI.

The reason was to expose the pipeline through HTTP endpoints and make it possible for the web UI to control it.

The API supports operations such as:

- running the pipeline
- getting information about a run
- validating a run
- getting summary information

Each pipeline execution gets a unique `run_id`.

---

# 38. Run IDs

A run ID identifies one particular pipeline execution.

For example:

```text
eccc8e1b-04e6-4887-8218-79319fcb733a
```

The UI and validation flow use this ID to refer to the correct run.

During testing I encountered:

```text
run_id not found
```

This happened because the requested run ID was not available in the current FastAPI process.

The current implementation keeps run information in memory.

So if the API process is restarted, the old in-memory run information is lost.

For this project that is acceptable, but a production version should persist run metadata.

---

# 39. Acceptance Validation

I then added the acceptance validation.

There are 10 checks:

1. Total rows
2. Distinct claims
3. Distinct patients
4. Distinct diagnosis codes
5. Patient P00042 diagnosis count
6. Patient P00042 row count
7. Diagnosis formatting
8. Service-date range
9. Patient ID completeness
10. Consecutive-run reproducibility

The first nine checks validate the final data.

The tenth check validates reproducibility.

---

# 40. The Tenth Test Case – Reproducibility

The tenth check compares the SHA256 output hash of the current completed run with the previous completed run.

The idea is:

```text
Run 1
  |
  v
Output A
  |
  v
Hash A

Run 2
  |
  v
Output B
  |
  v
Hash B

Hash A == Hash B
```

If the same input and same processing logic are used, the outputs should be identical.

Initially, this check did not pass in the UI.

---

# 41. Why the Tenth Check Initially Failed

The problem was not the transformation itself.

The problem was that the reproducibility test requires **two completed runs**.

If only one run exists:

```text
Current run = available
Previous run = not available
```

there is nothing to compare.

So I needed to change the application flow rather than change the data logic.
---

# 42. Web UI

I then created a simple web UI around the FastAPI backend.

The UI shows:

- project title
- pipeline status
- current run ID
- source summary
- final summary
- pipeline stages
- acceptance checks

The FastAPI backend runs on:

```text
http://127.0.0.1:8000
```

The UI is served separately.

I also handled CORS because the frontend and backend run on different ports.

The goal was that a new user should be able to use the project through the UI without manually running each Python source file.


---

# 43. UI Modification for Consecutive Runs

I modified the UI so the pipeline can be run consecutively.

The intended flow became:

```text
Run Pipeline
      |
      v
Run 1 completes
      |
      v
Run Pipeline again
      |
      v
Run 2 completes
      |
      v
Validate
      |
      v
Compare Run 2 with Run 1
```

While the pipeline is running, the UI shows the stages/cases as they complete.

This means the user can see progress instead of waiting with no information.

After two consecutive runs, the tenth check has both outputs available and the reproducibility comparison passes.

The final validation result is:

```text
10 / 10 PASS
OVERALL: PASS
```


---

# 44. Final Acceptance Result

After correcting the Source C version handling and then correcting the UI flow for the reproducibility check, the final validation passed all 10 checks.

The final expected values were:

```text
Final rows:              159,704
Distinct claims:          68,205
Distinct patients:        11,963
Distinct diagnoses:           44
Final columns:                15
```

Final validation:

```text
1. Total rows                         PASS
2. Distinct claims                   PASS
3. Distinct patients                 PASS
4. Distinct diagnosis codes          PASS
5. P00042 diagnosis count            PASS
6. P00042 total rows                 PASS
7. Diagnosis formatting              PASS
8. Service date range                PASS
9. Patient ID completeness           PASS
10. Consecutive-run reproducibility  PASS
```

Result:

```text
10 / 10 PASS
OVERALL: PASS
```

---

# 45. What I Was Not Completely Sure About

## Source B gender

I assumed:

```text
1 -> M
2 -> F
```

because the target needs a common representation.

I would verify this with source metadata in a production environment.

## Diagnosis dictionary

Four diagnosis codes were not found in the dictionary:

```text
Q998
R6889
T889
Z9989
```

I chose a LEFT JOIN so the claim rows remain even when a description is unavailable.

## Source C version

This was the main uncertainty.

My first implementation used:

```text
claim_ref + version
```

as the claim ID.

The complete pipeline then showed that the final row count and unique claim count did not match.

I investigated the source again and changed the handling so that the highest version for each `claim_ref` is retained.

This is an example of a decision that came from investigating the actual data and acceptance results rather than assuming the answer from the beginning.

---

# 46. What Went Wrong Along the Way

The biggest issues were data-understanding issues rather than syntax errors.

### Source A

Repeated diagnosis codes needed investigation before deciding how to handle them.

### Source B

I had to understand that missing referring NPIs were allowed and that `line_nbr` did not need to be carried into the final diagnosis-level grain.

### Source C

I initially used:

```text
claim_ref + version
```

as the claim ID.

I completed the source processing and the first complete harmonization.

Then the final row count and unique claim count did not match.

I went back and investigated the Source C version structure from several angles.

That led to the final version-handling decision.

### Validation

The first nine checks could pass while the tenth failed.

I then realized that reproducibility needs two consecutive completed runs.

So I changed the UI flow to support two runs before validation.

---

# 47. GitHub

After the project was working and the README/documentation were prepared, I pushed the complete project to GitHub.

Repository:

```text
https://github.com/lakshmimeherekshita/claims-harmonization.git
```

I initialized Git locally and added the project files.

The virtual environment was excluded using `.gitignore`.

I committed the initial project setup.

After changing the pipeline so that `data/processed` is created automatically, I committed that change as well.

The README was then added and pushed.

The project is now available as a complete GitHub repository.

---


# 48. What I Learned

The biggest thing I learned is that data harmonization is not simply:

```text
read files
+
rename columns
+
combine files
```

The difficult part is understanding the actual meaning and grain of each source.

Source A had eight diagnosis columns, so it needed diagnosis expansion.

Source B already had one diagnosis code per row, but `encounter_id` and `line_nbr` needed investigation to understand whether the line level affected the final grain.

Source C had multiple versions of the same `claim_ref`, and the correct version handling only became clear after the first complete pipeline did not match the expected claim count.

I also learned that missing data does not automatically mean bad data.

For example:

- missing referring NPI does not mean the claim should be removed
- missing secondary plan does not mean the claim should be removed when the field is not required
- empty diagnosis slots in Source A are not the same as missing patient IDs

I learned that intermediate row counts are extremely useful.

For example, Source A changes from:

```text
25,101
```

to:

```text
200,808
```

during diagnosis expansion and then to:

```text
68,993
```

after empty diagnoses are removed.

The `StageTracker` makes these changes easy to explain.

I also learned that the API and UI are separate layers from the actual data pipeline.

The pipeline does the data work.

FastAPI exposes that work through HTTP.

JavaScript calls the API.

HTML provides the page structure.

CSS controls how the page looks.

This separation made the project much easier to understand.

And one of the best decisions I made throughout the project was keeping `inspect_data.py`.

Whenever I had a new question, I could investigate it there first instead of changing the actual pipeline code immediately.

That helped me understand the data before making transformation decisions.

Most importantly, I learned that when an expected number does not match, I should investigate the data and its grain rather than simply change the code until the number matches.

---

# 49. Final Project Flow

The complete project now follows:

```text
                    RAW DATA
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
    SOURCE A       SOURCE B       SOURCE C
        |              |              |
        v              v              v
    Transform       Transform       Transform
        |              |              |
        +--------------+--------------+
                       |
                       v
               COMMON TARGET SCHEMA
                       |
                       v
                 COMBINE SOURCES
                       |
                       v
             LEFT JOIN DICTIONARY
                       |
                       v
              FINAL HARMONIZED DATA
                       |
                       v
                 ACCEPTANCE TESTS
                       |
                       v
                  10 / 10 PASS
                       |
                       v
                 STAGE TRACKER
                       |
                       v
                    FASTAPI
                       |
                       v
                      UI
                       |
                       v
                  GITHUB REPO
```

---

# 50. Final Summary

I started by inspecting the raw data one source at a time.

I used one file, `inspect_data.py`, throughout the investigation. This became my main place for asking questions about the data, checking counts, checking duplicates, checking the grain, and testing assumptions before changing the transformation code.

For Source A, I investigated the columns, missing patient IDs, service dates, eight diagnosis columns, repeated diagnoses, provider fields, plans, and financial fields. I transformed it to the required diagnosis-level grain.

For Source B, I investigated the encounter and line structure. In particular, I checked `encounter_id + line_nbr` and `encounter_id + dx_code` so I could understand whether line-level data affected the final diagnosis-level grain. I then validated the Source B grain and mapped the source to the common target schema.

For Source C, I initially created:

```text
CLAIM_ID = claim_ref + version
```

and completed the Source C transformation using that approach.

Then I completed the first version of harmonization.

The processed Source A, Source B, and Source C datasets were combined in `harmonize.py`, and only after the combination did I perform the diagnosis dictionary LEFT JOIN.

The first complete acceptance test then showed that the final row count and distinct claim count did not match the expected values.

I went back to Source C and investigated `claim_ref`, `version`, `seq`, and diagnosis combinations from multiple angles.

That investigation showed that treating every `claim_ref + version` as a separate final claim was causing the claim-count mismatch.

I changed Source C so that the highest version for each `claim_ref` is retained.

After the data pipeline was correct, I created `pipeline.py` to run Source A, Source B, Source C, and harmonization in one controlled sequence.

I added one shared `StageTracker` so I could see every stage and every row-count change.

Then I added FastAPI so the pipeline could be exposed through REST endpoints.

The UI was built with HTML, CSS, and JavaScript. HTML created the structure, CSS made it readable, and JavaScript connected the UI to FastAPI using HTTP requests.

I created and verified the UI.

During verification, I found that the tenth acceptance check was failing because:

```text
Two consecutive runs produce identical output
```

requires two completed pipeline runs.

I then changed the UI flow so the pipeline could be run twice and the second run could be compared with the first using the output hash.

After that, the final validation became:

```text
10 / 10 PASS
OVERALL: PASS
```

The final verified result is:

```text
159,704 final rows
68,205 distinct claims
11,963 distinct patients
44 distinct diagnosis codes
15 final columns
```

The project was then pushed to GitHub.

The main lesson from the project was:

> I should understand the source data and its grain first, build the transformation from that understanding, and when an expected result does not match, investigate the data before changing the code.

