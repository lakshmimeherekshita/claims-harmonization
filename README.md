# Claims Harmonization Pipeline

A Python-based healthcare claims harmonization project that processes claims data from three different sources, converts them into a common format, combines them, validates the final dataset, and provides a FastAPI backend with a simple web-based UI.

---

# How to Run This Project

If you are new to this project, follow the steps below **in the exact order**.

You do not need to understand the code before running the project.

---

## 1. Prerequisites

You need:

- Python **3.11.x or 3.12.x**
- Git

Check your Python version:

```bash
python --version
```

You should see something similar to:

```text
Python 3.11.x
```

or:

```text
Python 3.12.x
```

Check Git:

```bash
git --version
```

---

# 2. Clone the Repository

Open a terminal and run:

```bash
git clone <https://github.com/lakshmimeherekshita/claims-harmonization.git>
```

Then move into the project folder:

```bash
cd claims-harmonization
```

Replace `<https://github.com/lakshmimeherekshita/claims-harmonization.git>` with the URL of this GitHub repository.

---

# 3. Create a Virtual Environment

Creating a virtual environment keeps the project's Python packages separate from other projects on your computer.

Run:

```bash
python -m venv .venv
```

### Windows

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

After activation, you should see:

```text
(.venv)
```

at the beginning of your terminal.

---

# 4. Install the Required Packages

This project currently does **not** use a `requirements.txt` file.

With the virtual environment activated, run:

```bash
pip install pandas openpyxl fastapi uvicorn
```

Wait until all packages are installed successfully.

---

# 5. Check the Project Files

The repository should contain the following structure:

```text
claims-harmonization/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── api.py
│   ├── pipeline.py
│   ├── source_a.py
│   ├── source_b.py
│   ├── source_c.py
│   ├── harmonize.py
│   └── stage_tracker.py
│
├── ui/
│   └── index.html
│
└── README.md
```

The required input datasets are located inside:

```text
data/raw/
```

Do not rename or move the input files unless the corresponding paths in the Python code are also changed.

---

# 6. Start the FastAPI Backend

Make sure you are in the project root:

```text
claims-harmonization/
```

and your virtual environment is activated.

Run:

```bash
uvicorn src.api:app --reload
```

If the server starts successfully, you should see:

```text
Uvicorn running on http://127.0.0.1:8000
```

and:

```text
Application startup complete.
```

### Important

Keep this terminal open.

The FastAPI server must continue running while you use the web UI.

---

# 7. Check the FastAPI API

Open your browser and go to:

```text
http://127.0.0.1:8000/docs
```

This opens the FastAPI Swagger interface.

The project provides these API endpoints:

```text
POST /run
GET  /run/{run_id}/stages
GET  /run/{run_id}/validate
GET  /summary
```

You do not need to manually use these endpoints if you are using the web UI.

---

# 8. Start the Web UI

Open a **second terminal**.

Go to the project directory:

```bash
cd claims-harmonization
```

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Then start the UI server:

```bash
python -m http.server 5500 --directory ui
```

You should see something similar to:

```text
Serving HTTP on ... port 5500
```

Keep this terminal open too.

At this point you have:

```text
Terminal 1
FastAPI
http://127.0.0.1:8000
```

and:

```text
Terminal 2
Web UI
http://127.0.0.1:5500
```

---

# 9. Open the Web Application

Open your browser and go to:

```text
http://127.0.0.1:5500
```

You should see the:

**Claims Harmonization Pipeline**

dashboard.

---

# 10. Run the Project

On the web page, click:

```text
▶ Run Pipeline
```

You only need to click the button **once**.

The application automatically performs the complete workflow:

```text
Run Pipeline
     │
     ▼
First Pipeline Run
     │
     ▼
Source Summary
     │
     ▼
Pipeline Stages
     │
     ▼
Second Pipeline Run
     │
     ▼
Acceptance Checks
     │
     ▼
10 / 10 PASS
```

You do not need to manually run the pipeline twice.

---

# 11. What the Pipeline Does

The pipeline processes the three sources separately and then combines them.

```text
Source A
   │
   ▼
Source A Processing
   │
   ▼
Source B
   │
   ▼
Source B Processing
   │
   ▼
Source C
   │
   ▼
Source C Processing
   │
   ▼
Harmonization
   │
   ▼
Diagnosis Enrichment
   │
   ▼
Final Dataset
   │
   ▼
Validation
```

---

# 12. Expected Final Results

After a successful execution, the application should produce:

```text
Final Rows:          159,704
Distinct Claims:      68,205
Distinct Patients:    11,963
Distinct Diagnoses:       44
```

The source-level results are:

```text
Source A
Rows:              67,531
Distinct Claims:   25,101

Source B
Rows:              52,819
Distinct Claims:   23,516

Source C
Rows:              39,354
Distinct Claims:   19,588
```

The source rows combine to:

```text
67,531
+52,819
+39,354
-------
159,704
```

---

# 13. Acceptance Checks

The application performs 10 acceptance checks.

These checks verify:

1. Total rows in the final output
2. Distinct claims across all sources
3. Distinct patients
4. Distinct diagnosis codes
5. Patient `P00042` distinct diagnosis codes
6. Patient `P00042` total rows
7. Diagnosis-code formatting
8. Service-date range
9. Missing `PATIENT_ID`
10. Consecutive-run reproducibility

A successful execution should show:

```text
10 / 10 PASS
```

and:

```text
OVERALL: PASS
```

---

# 14. Reproducibility Check

The project verifies that two consecutive pipeline runs produce exactly the same output.

A SHA256 hash is generated for the final output.

The system compares:

```text
Run 1 SHA256
       =
Run 2 SHA256
```

If both outputs are identical, the reproducibility check passes.

The UI automatically performs the two required runs.

---

# 15. Source A

Source A contains source-specific processing such as:

- Removing records with missing `PATIENT_ID`
- Filtering service dates
- Expanding multiple diagnosis columns
- Removing empty diagnosis records
- Enforcing claim/diagnosis grain
- Mapping fields to the common target schema

Final verified result:

```text
Rows: 67,531
Distinct Claims: 25,101
```

---

# 16. Source B

Source B contains source-specific processing such as:

- Filtering service dates
- Normalizing diagnosis codes
- Validating claim/diagnosis grain
- Mapping gender values
- Mapping fields to the common target schema
- Final validation

Final verified result:

```text
Rows: 52,819
Distinct Claims: 23,516
```

---

# 17. Source C

Source C contains multiple versions of claims.

The pipeline keeps the highest version for each `claim_ref` before continuing with the remaining processing.

Source C processing includes:

- Latest-version selection
- Service-date filtering
- Diagnosis expansion
- Diagnosis normalization
- Grain validation
- Target-schema mapping

Final verified result:

```text
Rows: 39,354
Distinct Claims: 19,588
```

---

# 18. Harmonization

After Source A, Source B, and Source C have been processed, they are converted to the common target schema and combined.

The common schema contains:

```text
SRC
PATIENT_ID
BIRTH_YEAR
GENDER
ZIP3
CLAIM_ID
SERVICE_DATE
DIAGNOSIS_CODE
PLACE_OF_SERVICE
RENDERING_NPI
REFERRING_NPI
BILLING_NPI
PRIMARY_PLAN_ID
BILLED_AMOUNT
```

A diagnosis dictionary is then used to add:

```text
DIAGNOSIS_DESC
```

The final dataset therefore contains:

```text
15 columns
```

---

# 19. Pipeline Stage Tracking

The project includes a stage tracker that records what happens at each processing stage.

For every stage, the system records:

- Input row count
- Output row count
- Change in row count
- Reason for the change

This makes it possible to see how the dataset changes throughout the pipeline.

---

# 20. Run the Python Pipeline Directly

The web UI is the recommended way to run the complete project.

However, if you want to run the underlying Python pipeline directly, run this command from the project root:

```bash
python -m src.pipeline
```

A successful execution should end with:

```text
Final rows: 159704
Final columns: 15
```

The processed datasets are written to:

```text
data/processed/
```

---

# 21. Troubleshooting

## Python command is not recognized

Install Python 3.11.x or 3.12.x and make sure Python is added to PATH.

Check again:

```bash
python --version
```

---

## FastAPI is not installed

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Then run:

```bash
pip install pandas openpyxl fastapi uvicorn
```

---

## `ModuleNotFoundError`

Make sure you are running commands from the project root:

```text
claims-harmonization/
```

Use:

```bash
uvicorn src.api:app --reload
```

Do not run the command from inside the `src` folder.

---

## FastAPI does not start

Check that the required packages are installed:

```bash
pip install pandas openpyxl fastapi uvicorn
```

Then run:

```bash
uvicorn src.api:app --reload
```

---

## UI does not connect to the API

Make sure both terminals are running.

### Terminal 1

```bash
uvicorn src.api:app --reload
```

### Terminal 2

```bash
python -m http.server 5500 --directory ui
```

Then open:

```text
http://127.0.0.1:5500
```

---

## Port 8000 is already in use

Stop the existing FastAPI server and start it again.

Alternatively:

```bash
uvicorn src.api:app --reload --port 8001
```

If you change the API port, the API URL in `ui/index.html` must also be changed.

---

## `run_id not found`

Run IDs are stored in memory while the FastAPI server is running.

If FastAPI is restarted, previous run IDs are no longer available.

Simply click:

```text
▶ Run Pipeline
```

again.

---

# 22. Quick Start

If Python and Git are already installed, the shortest setup is:

### Clone

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd claims-harmonization
```

### Create environment

```bash
python -m venv .venv
```

### Activate environment — Windows

```powershell
.venv\Scripts\activate
```

### Install packages

```bash
pip install pandas openpyxl fastapi uvicorn
```

### Terminal 1 — Start FastAPI

```bash
uvicorn src.api:app --reload
```

### Terminal 2 — Start UI

```bash
python -m http.server 5500 --directory ui
```

### Open the UI

```text
http://127.0.0.1:5500
```

### Click

```text
▶ Run Pipeline
```

### Expected result

```text
10 / 10 PASS
OVERALL: PASS
```

---

# 23. Final Verified Results

The complete project has been tested end-to-end.

```text
Source A Processing          PASS
Source B Processing          PASS
Source C Processing          PASS
Harmonization                PASS
Final Dataset                PASS
FastAPI Backend              PASS
Web UI                       PASS
Acceptance Validation        PASS
Reproducibility              PASS
```

Final verified output:

```text
Final Rows:          159,704
Distinct Claims:      68,205
Distinct Patients:    11,963
Distinct Diagnoses:       44
```

Final validation:

```text
10 / 10 PASS
OVERALL: PASS
```

---

# 24. Done!

If you are a new user, you only need to remember these three things:

### Start FastAPI

```bash
uvicorn src.api:app --reload
```

### Start the UI

```bash
python -m http.server 5500 --directory ui
```

### Open the UI

```text
http://127.0.0.1:5500
```

Then click:

```text
▶ Run Pipeline
```

The application handles the rest.
