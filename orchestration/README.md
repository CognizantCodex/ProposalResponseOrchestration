# RFP Agent Orchestration

This package implements the MVP workflow in `problem.md`:

1. `ReceiverAgent` validates and extracts the RFP, computes a SHA-256 fingerprint, rejects duplicates, and records progress in Excel.
2. `AgentOrchestrator` owns state, routing, retries, failure handling, and the durable run log.
3. `ClassifierAgent` extracts requirements, categories, commercial questions, and evidence-backed winning themes.
4. `RequirementAgent` creates the requirement brief and maps each requirement to a service line and proposed owner.
5. `QuestionnaireAgent` creates the open-question list and returns the consolidated workflow state to the orchestrator.

Model-backed agents use the OpenAI Responses API with strict JSON schemas. Requests set `store=False`; confirm the target OpenAI project's retention and governance settings before using customer material.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-project-key"
python -m orchestration.cli --account WellsFargo --file "RFP/WellsFargo/sample-rfp.pdf"
```

The run writes `data/RFP_Status_Tracker.xlsx` and one JSON state file under `data/runs/`. The ReceiverAgent also accepts a GitHub blob URL (for example, the Bank 1 DOCX on the `develop` branch). To expose the dashboard event bridge, run `python -m orchestration.http_server --port 8000` and set the dashboard's `VITE_AGENT_API_BASE` to that URL.

For a validated `Bank 1` intake, ReceiverAgent creates `Customer RFP Documentation/Bank 1/<RFP name>/` with `Case Study and Reference`, `Customer Documents`, `Pricing`, `Questionnaire`, `Response`, and `TO` subfolders. Replays are rejected before creating or changing a workspace.

## Safety and review boundary

Outputs are working drafts. Human owners must review requirement coverage, ownership, evidence, commercial terms, and all customer commitments before anything is shared or submitted.

