# Proposal Response Orchestration Architecture

## 1. Purpose and scope

This repository contains two cooperating parts:

1. A React/Vite dashboard that gives proposal teams an account-centric view of RFP documents, lifecycle status, service-line assignments, and working selections.
2. A Python orchestration package that validates and extracts an RFP, detects duplicates, calls specialized agents with strict JSON schemas, records durable state, and produces requirements, ownership, and questionnaire outputs.

The current implementation is a hackathon/MVP architecture. It establishes the core workflow and contracts, while production integrations such as an authenticated application API, CRM/email triggers, SharePoint, ODS, Teams, enterprise identity, and approval gates remain future work.

## 2. System context

    Proposal user
         |
         v
    React/Vite Dashboard
         |  reads account/status Markdown and GitHub document metadata
         |  emits a browser event when ReceiverAgent is requested
         v
    Application API / job boundary (production integration point)
         |
         v
    AgentOrchestrator
         |
         +--> ReceiverAgent
         +--> ClassifierAgent
         +--> RequirementAgent
         +--> QuestionnaireAgent
         |
         +--> JSON run state
         +--> Excel progress tracker
         +--> OpenAI Responses API
         +--> category and SLS knowledge sources

Important current boundary: the dashboard's **Run Agent Receiver** action records UI state and emits the `agent-receiver:run` browser event, but it does not yet invoke the Python orchestration package. A backend API or worker integration is required to make this an end-to-end production workflow.

## 3. Repository structure

| Path | Purpose |
| --- | --- |
| `Dashboard/` | React 18 and Vite UI application. |
| `Dashboard/src/App.jsx` | Account selection, repository document listing, RFP cards, service-line inputs, and browser-local draft handling. |
| `Dashboard/AccountList.md` and `Dashboard/AccountsList.md` | Account options imported by the UI at build time. |
| `Dashboard/RFPStatus.md` | Markdown table imported and rendered as RFP portfolio data. |
| `Customer RFP Documentation/<Account>/` | Account-scoped RFP source documents. |
| `orchestration/` | Python agents, orchestration, schemas, configuration, extraction, knowledge loading, tracking, and CLI. |
| `knowledge/` | Optional category and SLS ownership references. |
| `data/runs/` | Durable JSON state, one file per run. Created at runtime. |
| `data/rfp_progress.xlsx` | Excel progress and SHA-256 duplicate tracker. Created at runtime. |
| `tests/` | Automated orchestration and duplicate-detection coverage. |

## 4. UI application architecture

The UI is a client-side React application built with Vite.

### 4.1 Inputs and account context

The dashboard captures:

- Business unit and sub-business unit
- Account name
- CP
- CRM
- Winzone ID
- TCV
- Service-line offerings
- SLS email and phone information

Account names are parsed from numbered Markdown lists and de-duplicated. Business units, sub-business units, service lines, and offerings are currently defined in the UI source.

### 4.2 Repository document access

For the selected account, the UI calls the GitHub Contents API for:

`Customer RFP Documentation/<Account>?ref=develop`

It displays file type, size, GitHub view/download links, and excludes `.gitkeep`. This is a direct browser-to-GitHub read path and therefore depends on repository visibility, browser access, API rate limits, and CORS behavior. Production use should place repository or SharePoint access behind an authenticated application service.

### 4.3 Receiver trigger boundary

When a user selects **Run Agent Receiver**, the UI:

1. Marks the selected GitHub blob SHA as started.
2. Records the account, document name, document SHA, and start time in component state.
3. Dispatches an `agent-receiver:run` custom browser event.
4. Reveals the RFP portfolio section.

No durable job is created by the UI today. A production adapter should receive this event through an API call, resolve or download the selected document, enqueue the run, and return a run ID that the UI can poll or subscribe to.

### 4.4 Draft state

**Save draft** writes account and assignment selections to browser `localStorage` under `bcm-sls-rfp-draft`. This state is device- and browser-specific, is not shared, and is not an authoritative system of record.

## 5. Orchestration runtime

The Python entry point is:

`python -m orchestration.cli --account <Account> --file <RFP path>`

The CLI loads environment-based settings, creates `AgentOrchestrator`, runs the pipeline, and prints the final `PipelineState` as JSON.

### 5.1 Pipeline sequence

| Step | Agent | Primary input | Primary output | Success event |
| --- | --- | --- | --- | --- |
| 1 | AgentOrchestrator | Account and source path | Run ID and initial state | `STARTED` |
| 2 | ReceiverAgent | File bytes and account | Extracted text and `RfpMetadata` | `VALIDATED` |
| 3 | ClassifierAgent | Extracted text and category reference | `ClassificationResult` | `CLASSIFIED` |
| 4 | RequirementAgent | Classification and SLS reference | `RequirementsResult` | `OWNERS_MAPPED` |
| 5 | QuestionnaireAgent | Classification and requirements result | `QuestionnaireResult` | `QUESTIONNAIRE_READY` |
| 6 | AgentOrchestrator | Completed agent outputs | Final saved state and tracker update | `COMPLETED` |

The orchestrator saves state before processing and after every meaningful event. This makes the event history and completed outputs available even when a later step fails.

## 6. Agent responsibilities and contracts

### 6.1 AgentOrchestrator

Responsibilities:

- Generates a UUID run ID.
- Owns routing and sequencing.
- Persists the current state and event history.
- Applies retry policy to model-backed agents.
- Updates the Excel tracker on completion or failure.
- Handles duplicates as a terminal, non-exceptional pipeline result.
- Re-raises unexpected failures after recording them.

Retry behavior is controlled by `MAX_AGENT_RETRIES`. Each model-backed attempt records an attempt number and a running/retry event. Backoff is exponential and capped at four seconds.

### 6.2 ReceiverAgent

Responsibilities:

- Confirms the source path is a file.
- Reads the original bytes.
- Computes a SHA-256 digest.
- Extracts text using the file-type-specific reader.
- Rejects documents with no extractable text.
- Searches the Excel tracker for a prior non-failed row with the same digest.
- Writes ingestion metadata and duplicate status to the tracker.

Supported formats:

| Format | Extraction behavior | Unit count |
| --- | --- | --- |
| PDF | Text from each page using `pypdf` | Page count |
| DOCX | Paragraphs plus table rows using `python-docx` | Section count, minimum 1 |
| PPTX | Text-bearing shapes using `python-pptx` | Slide count |
| TXT | UTF-8 text | 1 |
| Markdown | UTF-8 text | 1 |

`RfpMetadata` contains run ID, account, source path, filename, file type, byte size, SHA-256 digest, unit count, word count, ingestion timestamp, and an optional duplicate run ID.

### 6.3 ClassifierAgent

The classifier receives the account, extracted RFP text, and category reference. It uses the OpenAI Responses API with a strict JSON schema.

Output fields:

- Summary
- Categories
- Evidence-backed winning themes
- Requirements
- Commercial questions

Each requirement includes a stable requirement ID, title, description, mandatory flag, source hint, and category. The instructions require source traceability and prohibit marking an item mandatory unless the source does so.

### 6.4 RequirementAgent

The requirement agent receives the complete classification plus the approved SLS reference.

Output fields:

- Concise requirement brief
- Ownership map
- Evidence gaps
- Clarification gaps

Each ownership assignment contains requirement ID, primary service line, proposed owner, rationale, and confidence (`high`, `medium`, or `low`). The agent is instructed to use only the supplied reference and return `UNASSIGNED` with low confidence when no qualified owner exists.

### 6.5 QuestionnaireAgent

The questionnaire agent receives the classification and requirement outputs.

Output fields:

- Open questions
- Response summary

Each question contains question ID, related requirement ID, question text, proposed owner, and status. Allowed statuses are `OPEN`, `ANSWERED`, and `BLOCKED`. Newly generated questions are expected to be `OPEN`.

## 7. Structured model integration

`OpenAIJsonClient` is an adapter over the OpenAI Responses API.

- The model is selected with `OPENAI_MODEL`.
- The full agent payload is serialized as JSON.
- Each request supplies a named strict JSON schema.
- `store=False` is set on model requests.
- Empty model output raises an error.
- Parsed responses are converted into typed Python dataclasses.

Strict schemas set `additionalProperties: false` and enumerate required fields. This prevents downstream agents from receiving loosely shaped results, but semantic correctness still requires human review.

## 8. State, events, and persistence

### 8.1 PipelineState

The durable run object contains:

- Run ID, account, and source path
- Current status and current agent
- Attempt count per agent
- Timestamped event history
- Receiver metadata
- Classification output
- Requirement/ownership output
- Questionnaire output
- Final error, when present

### 8.2 JSON state store

`StateStore` writes `data/runs/<run-id>.json`. It first writes a temporary file and then replaces the target, reducing the chance of leaving a partially written state file.

The current code persists durable checkpoints but does not yet expose a resume method. Production recovery should load the last valid state and continue from the first incomplete step using idempotent agent operations.

### 8.3 Excel tracker

The workbook contains:

- Run ID
- Account
- File name
- Source path
- SHA-256
- Received timestamp
- Status
- Current agent
- Duplicate-of run ID
- Error

The sheet is created automatically, freezes the header row, and adds an auto-filter. Duplicate detection ignores prior rows whose status is `FAILED`.

The workbook is suitable for an MVP or single-process workflow. Concurrent production workers require locking or migration to a transactional database.

## 9. Knowledge loading and fallbacks

Category reference resolution:

1. Read `CATEGORY_PATH` when the file exists.
2. Otherwise use the built-in default category list.

SLS ownership resolution:

1. Read `SLS_CONTACT_PATH` when the Markdown file exists.
2. Otherwise read all worksheets from `SLS_EMPLOYEE_MASTER_PATH`.
3. If neither exists, instruct the agent to return `UNASSIGNED` owners.

Recommended knowledge content includes approved category definitions, service-line ownership, current contacts, reusable evidence, approval state, source and expiry dates, customer restrictions, and account-specific confidentiality rules.

## 10. Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | None | Project credential used by the OpenAI client. |
| `OPENAI_MODEL` | `gpt-5.5` | Model used by the structured agents. |
| `RFP_ROOT` | `RFP` | Root for local RFP documents. |
| `RFP_TRACKER_PATH` | `data/rfp_progress.xlsx` | Excel tracker path. |
| `RFP_STATE_DIR` | `data/runs` | JSON state directory. |
| `CATEGORY_PATH` | `knowledge/category.md` | Category reference. |
| `SLS_CONTACT_PATH` | `knowledge/SLS point of contact.md` | Preferred SLS reference. |
| `SLS_EMPLOYEE_MASTER_PATH` | `knowledge/Synthetic_Service_Line_Employee_Master.xlsx` | SLS fallback workbook. |
| `MAX_AGENT_RETRIES` | `2` | Additional attempts for each model-backed agent. |

Runtime dependencies are declared in `requirements.txt`: OpenAI SDK, OpenPyXL, Pydantic, pypdf, python-docx, and python-pptx.

## 11. Failure and duplicate behavior

| Condition | Behavior |
| --- | --- |
| Missing source file | Pipeline records failure and raises `FileNotFoundError`. |
| Unsupported extension | Extraction raises a validation error. |
| No extractable text | Receiver raises a validation error. |
| Existing SHA-256 | Tracker row is marked `DUPLICATE`; state records the original run ID; downstream agents do not run. |
| Agent or model failure | Attempt and retry events are saved; final failure updates the tracker and state, then propagates. |
| Successful run | Tracker is marked `COMPLETED`; all outputs and events are saved. |

## 12. Security, governance, and human review

- Never commit `OPENAI_API_KEY` or other credentials.
- Confirm model access, retention, regional processing, and project governance before using customer content.
- `store=False` is requested for model calls; this does not replace organizational review of data-handling requirements.
- Account data and evidence must be separated by authorization scope.
- Prior responses must carry approval, reuse, expiration, and customer-restriction metadata.
- Logs and state files may contain customer-sensitive content and require access control, encryption, retention, and deletion policies.
- Agent outputs are working drafts. Human owners must approve requirements, ownership, evidence, commercials, legal language, and customer commitments before submission.

## 13. Testing

`tests/test_orchestrator.py` uses a deterministic fake structured-LLM implementation and a temporary filesystem. It verifies:

1. A valid Markdown RFP completes the full pipeline.
2. Classification, ownership, and questionnaire outputs are accepted.
3. A second run of the same bytes is detected as a duplicate.
4. The duplicate state references the original run.

Additional production-grade coverage should include every file extractor, malformed and oversized inputs, schema failures, retry exhaustion, empty extraction, workbook locking, interrupted state writes, authorization boundaries, UI-to-API integration, and concurrent submissions.

## 14. Production evolution

Recommended next steps:

1. Add an authenticated API between the dashboard and the Python orchestration package.
2. Replace the browser custom event with a durable job request returning a run ID.
3. Add a worker or queue for asynchronous processing and retry isolation.
4. Expose run status and event history through polling, server-sent events, or WebSockets.
5. Move tracking to a transactional store while retaining Excel only as an export when required.
6. Store source and generated artifacts in an approved document repository such as SharePoint.
7. Integrate CRM/email triggers, ODS state, Teams notifications, and human approval gates.
8. Add enterprise identity, account-level authorization, audit logging, secrets management, observability, retention, and disaster recovery.
9. Add explicit resume/idempotency semantics for interrupted runs.
10. Version JSON schemas and prompts so saved runs remain reproducible.

## 15. Key references

- [Dashboard](Dashboard/README.md)
- [Setup guide](orchestration/README.md)
- [Required inputs](orchestration/INPUTS.md)
- [CLI](orchestration/cli.py)
- [Orchestrator](orchestration/orchestrator.py)
- [Models and pipeline state](orchestration/models.py)
- [Receiver agent](orchestration/receiver_agent.py)
- [Classifier agent](orchestration/classifier_agent.py)
- [Requirement agent](orchestration/requirement_agent.py)
- [Questionnaire agent](orchestration/questionnaire_agent.py)
- [Environment template](.env.example)
- [Automated test](tests/test_orchestrator.py)
