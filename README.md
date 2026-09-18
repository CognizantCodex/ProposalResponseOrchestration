# Proposal Response Orchestration

Proposal Response Orchestration is an MVP for receiving customer RFP documents, extracting and classifying requirements, mapping work to service lines, creating an open-question questionnaire, and exposing the workflow to a React dashboard.

The solution combines:

- A React + Vite dashboard for account context, repository documents, RFP status, service-line assignments, and draft data.
- A Python orchestration service with Receiver, Classifier, Requirement, and Questionnaire agents.
- The OpenAI Responses API with structured JSON outputs for model-backed processing.
- Durable JSON run state and an Excel tracker for progress and duplicate detection.
- A small REST bridge that lets the dashboard start a run and retrieve its status.

For the detailed component and data-flow view, see [ARCHITECTURE.md](ARCHITECTURE.md). Agent implementation notes are in [orchestration/README.md](orchestration/README.md).

## Repository layout

| Path | Purpose |
| --- | --- |
| `Dashboard/` | React + Vite web application |
| `orchestration/` | Python agents, orchestration, REST bridge, document extraction, state, and tracking |
| `tests/` | Python orchestration tests |
| `knowledge/` | Example category and service-line reference data |
| `Customer RFP Documentation/` | Account-specific source documents and generated collaboration folders |
| `data/runs/` | Generated JSON state for each run |
| `data/RFP_Status_Tracker.xlsx` | Generated run and duplicate tracker |
| `.env.example` | Supported backend configuration |
| `PROMPTS.md` and `prompts.md` | Recorded and reusable team prompts |

## Prerequisites

- Git
- Python 3.10 or later
- Node.js 18 or later with npm
- An OpenAI API key for real model-backed runs

The dashboard can be viewed without an API key. Running the full Python pipeline requires the API key unless a test double is supplied, as in the automated tests.

## Full local setup

### 1. Clone and select the development branch

```bash
git clone https://github.com/CognizantCodex/ProposalResponseOrchestration.git
cd ProposalResponseOrchestration
git switch develop
```

### 2. Configure and install the Python service

Create a virtual environment and install the backend dependencies.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

The Python application reads environment variables directly; it does not automatically load the `.env` file. Export the values in your shell or use your preferred environment loader.

Minimum PowerShell configuration:

```powershell
$env:OPENAI_API_KEY = "your-project-api-key"
$env:OPENAI_MODEL = "gpt-5.5"
```

Minimum macOS/Linux configuration:

```bash
export OPENAI_API_KEY="your-project-api-key"
export OPENAI_MODEL="gpt-5.5"
```

Optional backend settings:

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_MODEL` | `gpt-5.5` | Model used by the model-backed agents |
| `RFP_ROOT` | `RFP` | Local source-document root |
| `CUSTOMER_RFP_ROOT` | `Customer RFP Documentation` | Account and RFP collaboration workspace |
| `RFP_TRACKER_PATH` | `data/RFP_Status_Tracker.xlsx` | Excel progress and duplicate tracker |
| `RFP_STATE_DIR` | `data/runs` | Durable JSON run-state directory |
| `CATEGORY_PATH` | `knowledge/category.md` | Requirement category reference |
| `SLS_CONTACT_PATH` | `knowledge/SLS point of contact.md` | Service-line contact reference |
| `SLS_EMPLOYEE_MASTER_PATH` | `knowledge/Synthetic_Service_Line_Employee_Master.xlsx` | Optional service-line employee reference |
| `MAX_AGENT_RETRIES` | `2` | Retries after the first attempt for each model-backed agent |

The repository includes example knowledge files. Copy or rename them to the configured paths, or update the environment variables to point directly to the example files.

### 3. Start the Python API

From the repository root:

```bash
python -m orchestration.http_server --host 127.0.0.1 --port 8000
```

The API is then available at `http://127.0.0.1:8000`.

### 4. Install and start the dashboard

In a second terminal:

Windows PowerShell:

```powershell
cd Dashboard
npm install
"VITE_AGENT_API_BASE=http://127.0.0.1:8000" | Set-Content .env.local
npm run dev
```

macOS or Linux:

```bash
cd Dashboard
npm install
printf 'VITE_AGENT_API_BASE=http://127.0.0.1:8000\n' > .env.local
npm run dev
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173`. Select an account and a repository document, then choose **Run Agent Receiver** to create a backend run.

The dashboard reads its account, RFP, contact, category, and frontier-model seed data from Markdown files in `Dashboard/`. It also retrieves customer document listings from the repository's `develop` branch.

### 5. Run the pipeline from the CLI (optional)

The CLI accepts PDF, DOCX, PPTX, TXT, and Markdown input:

```bash
python -m orchestration.cli --account "Bank 1" --file "Customer RFP Documentation/Bank 1/Bank 1 - Oracle Java Migration RFP 2026.docx"
```

The command prints the final pipeline state as JSON. It also writes the tracker workbook and a run-state JSON file.

### 6. Run tests and production builds

Run the Python tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

Build the dashboard:

```bash
cd Dashboard
npm run build
npm run preview
```

The production bundle is written to `Dashboard/dist/`.

## Processing flow

1. The Receiver agent downloads or opens the document, extracts text, computes a SHA-256 fingerprint, rejects duplicates, and records the intake.
2. The Classifier agent produces a summary, categories, winning themes, requirements, and commercial questions.
3. The Requirement agent creates a requirement brief and maps requirements to service lines and proposed owners.
4. The Questionnaire agent creates open questions and a response summary.
5. The orchestrator persists status, attempts, events, outputs, and failures after each stage.

For a validated Bank 1 intake, the Receiver agent also creates an RFP workspace containing `Case Study and Reference`, `Customer Documents`, `Pricing`, `Questionnaire`, `Response`, and `TO` folders.

A repeated file with the same SHA-256 fingerprint is marked `DUPLICATE` and is not registered as a second intake.

## API documentation

### Base URL

Local default: `http://127.0.0.1:8000`

The current MVP API has permissive CORS and no authentication. Do not expose it directly to an untrusted network.

### Create a run

`POST /runs`

Starts processing in a background thread and immediately returns a run ID.

Request body:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `account` | string | Yes | Account name used for tracking and workspace routing |
| `source_url` | string | One source field | HTTP(S) document URL; GitHub blob URLs are converted to raw URLs |
| `source_path` | string | One source field | Path accessible from the API process |

If both source fields are supplied, `source_url` takes precedence. A remote URL must end with a supported file extension.

Example request using a repository document:

```bash
curl -X POST http://127.0.0.1:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "account": "Bank 1",
    "source_url": "https://github.com/CognizantCodex/ProposalResponseOrchestration/blob/develop/Customer%20RFP%20Documentation/Bank%201/Bank%201%20-%20Oracle%20Java%20Migration%20RFP%202026.docx"
  }'
```

Example request using a server-local file:

```json
{
  "account": "Bank 1",
  "source_path": "Customer RFP Documentation/Bank 1/Bank 1 - Oracle Java Migration RFP 2026.docx"
}
```

Successful response — `202 Accepted`:

```json
{
  "run_id": "7d407129-1f14-4f22-93f0-95f68d8cc4b9",
  "status": "STARTED"
}
```

Invalid request — `400 Bad Request`:

```json
{
  "error": "account and source_url/source_path are required"
}
```

### Get run status

`GET /runs/{run_id}`

Returns the durable pipeline state. Poll this endpoint until `status` is `COMPLETED`, `DUPLICATE`, or `FAILED`.

Example request:

```bash
curl http://127.0.0.1:8000/runs/7d407129-1f14-4f22-93f0-95f68d8cc4b9
```

Example completed response:

```json
{
  "run_id": "7d407129-1f14-4f22-93f0-95f68d8cc4b9",
  "account": "Bank 1",
  "source_path": "Customer RFP Documentation/Bank 1/sample.md",
  "status": "COMPLETED",
  "current_agent": "orchestrator",
  "attempts": {
    "classifier": 1,
    "requirement": 1,
    "questionnaire": 1
  },
  "events": [
    {
      "at": "2026-09-17T20:45:00+00:00",
      "agent": "orchestrator",
      "status": "STARTED",
      "message": "Pipeline created"
    },
    {
      "at": "2026-09-17T20:45:08+00:00",
      "agent": "orchestrator",
      "status": "COMPLETED",
      "message": "All agents completed"
    }
  ],
  "metadata": {
    "file_name": "sample.md",
    "file_type": "md",
    "sha256": "9d7d...",
    "word_count": 42,
    "duplicate_of": null
  },
  "classification": {
    "summary": "Cloud migration request",
    "categories": ["Cloud migration"],
    "winning_themes": ["Traceable migration plan"],
    "requirements": [
      {
        "requirement_id": "REQ-001",
        "title": "Migration plan",
        "description": "Provide a phased migration plan",
        "mandatory": true,
        "source_hint": "Requirements",
        "category": "Cloud migration"
      }
    ],
    "commercial_questions": []
  },
  "requirements": {
    "requirement_brief": "One mandatory cloud migration requirement.",
    "ownership_map": [
      {
        "requirement_id": "REQ-001",
        "primary_service_line": "CIS",
        "proposed_owner": "Cloud Architect",
        "rationale": "Cloud migration scope",
        "confidence": "high"
      }
    ],
    "evidence_gaps": [],
    "clarification_gaps": []
  },
  "questionnaire": {
    "open_questions": [
      {
        "question_id": "Q-001",
        "requirement_id": "REQ-001",
        "question": "Which workloads are in scope?",
        "proposed_owner": "Cloud Architect",
        "status": "OPEN"
      }
    ],
    "response_summary": "One clarification is required."
  },
  "error": null
}
```

The example is abbreviated: receiver metadata also includes file size, unit count, ingestion time, and source information, while the event list normally contains an entry for every pipeline stage.

Unknown run — `404 Not Found`:

```json
{
  "error": "Run not found"
}
```

Unknown route — `404 Not Found`:

```json
{
  "error": "Not found"
}
```

## Generated data and review boundary

Run state and tracker files are generated locally and may contain customer-derived information. Keep secrets out of source control, apply the required data-handling policy, and confirm the configured OpenAI project's retention and governance settings before processing customer material.

Agent outputs are working drafts. Human owners must review requirement coverage, evidence, ownership, commercial terms, and every customer commitment before anything is shared or submitted.

## Production considerations

The REST bridge is intentionally minimal. A production deployment should add authentication and authorization, TLS, restricted CORS, validated request DTOs, a durable job queue, transactional persistence, account isolation, secrets management, observability, rate limits, and explicit approval controls for enterprise write actions.
