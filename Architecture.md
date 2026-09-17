# Proposal Response Orchestration Architecture

## Scope

The solution consists of an operator-facing UI app and a durable, agent-based orchestration service for processing customer RFPs. The UI app collects the account and RFP inputs, starts or monitors a run, and presents the resulting requirements, questions, ownership, evidence gaps, and status. The orchestration layer validates inputs, coordinates specialized agents, persists progress, and handles retries and failures.

## High-level flow

```text
UI app
  |
  v
AgentOrchestrator
  |
  +--> ReceiverAgent ------> validated text + SHA-256 duplicate check
  |
  +--> ClassifierAgent ----> requirements, categories, commercial questions,
  |                          and winning themes
  |
  +--> RequirementAgent ---> requirement brief, SLS ownership mapping,
  |                          and evidence gaps
  |
  +--> QuestionnaireAgent -> open questions, owners, and consolidated status
  |
  v
Durable run state + Excel progress tracking + JSON outputs
```

The diagram is conceptual: the orchestrator owns sequencing, durable state, retries, and error handling while each specialist produces a schema-validated result.

## Components

| Component | Responsibility |
| --- | --- |
| **UI app** | Captures the account name and RFP, starts orchestration, and exposes progress and agent results to the user. |
| **AgentOrchestrator** | Routes work to agents, maintains durable state, retries recoverable failures, and handles errors. |
| **ReceiverAgent** | Validates the input file, extracts text, computes a SHA-256 hash for duplicate detection, and updates Excel tracking. |
| **ClassifierAgent** | Identifies requirements and categories, surfaces commercial questions, and records winning themes. |
| **RequirementAgent** | Produces the requirement brief, maps SLS ownership, and identifies evidence gaps. |
| **QuestionnaireAgent** | Generates open questions, assigns owners, and consolidates questionnaire status. |

## Agent contracts

- Agent outputs use strict JSON schemas.
- The orchestrator validates every agent response against its schema before advancing the run.
- Invalid or incomplete responses are treated as errors and are eligible for the configured retry policy.
- Durable state enables a run to be resumed without losing completed work.
- Errors and final run status are recorded for UI display and troubleshooting.

## Document ingestion

The ReceiverAgent supports:

- PDF
- DOCX
- PPTX
- Markdown
- Plain text

It validates the file, extracts text, computes a SHA-256 digest, and uses the digest to detect duplicate submissions before downstream processing.

## Persistence and outputs

A run requires a writable location for:

- `data/rfp_progress.xlsx` — Excel progress and duplicate-tracking workbook
- `data/runs/*.json` — durable run state and schema-validated agent outputs

## Required inputs

1. `OPENAI_API_KEY`
2. Access to the model configured by `OPENAI_MODEL`
3. An account name
4. An RFP in PDF, DOCX, PPTX, TXT, or Markdown format
5. Python dependencies from `requirements.txt`
6. A writable `data` location for the files listed above

## Recommended knowledge inputs

- `knowledge/category.md`
- `knowledge/SLS point of contact.md`, or the synthetic employee workbook
- Approved prior RFP responses and capability evidence
- Account lookup metadata and confidentiality rules

## Key implementation files

- [Setup guide](orchestration/README.md)
- [Required inputs](orchestration/INPUTS.md)
- [Orchestrator](orchestration/orchestrator.py)
- [Environment template](.env.example)
- [Automated test](tests/test_orchestrator.py)

## Verification

The repository includes automated coverage for orchestration and duplicate detection. These tests verify the end-to-end coordination path and the ReceiverAgent's SHA-256 duplicate handling.
