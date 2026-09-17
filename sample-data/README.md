# Sample Endpoint Dataset

This directory contains 20 mock records for the Proposal Response Orchestration REST API and synthetic RFP inputs for the scenarios that require documents.

## Contents

- `mock-runs.json` - machine-readable requests and expected results.
- `rfps/mock-01-*.md` through `rfps/mock-15-*.md` - unique successful-input documents.
- `rfps/mock-17-empty.md` - empty-text failure case.
- `rfps/mock-18-unsupported.csv` - unsupported-format failure case.

All content is synthetic and contains no customer-confidential information.

## Prerequisites

1. Set `OPENAI_API_KEY` and `OPENAI_MODEL`.
2. Start the API with `python -m orchestration.http_server --port 8000`.
3. Use `http://127.0.0.1:8000` as the base URL.
4. For a `202` response, capture `run_id` and poll `GET /runs/{run_id}` until the state reaches `COMPLETED`, `DUPLICATE`, or `FAILED`.
5. Run MR-001 before MR-016 with the same tracker to exercise duplicate detection.

## Expected-result summary

| Record | Scenario | Account | Expected result |
| --- | --- | --- | --- |
| MR-001 | Successful Cloud Migration intake | Bank 1 | 202 -> COMPLETED |
| MR-002 | Successful Application Modernization intake | Bank 2 | 202 -> COMPLETED |
| MR-003 | Successful Quality Engineering Automation intake | Bank 3 | 202 -> COMPLETED |
| MR-004 | Successful AI and Analytics intake | Bank 4 | 202 -> COMPLETED |
| MR-005 | Successful Infrastructure Transformation intake | Bank 5 | 202 -> COMPLETED |
| MR-006 | Successful Cybersecurity Services intake | Bank 6 | 202 -> COMPLETED |
| MR-007 | Successful ERP Transformation intake | Bank 7 | 202 -> COMPLETED |
| MR-008 | Successful CRM Modernization intake | Bank 8 | 202 -> COMPLETED |
| MR-009 | Successful Process Automation intake | Bank 9 | 202 -> COMPLETED |
| MR-010 | Successful Digital Engineering intake | Bank 10 | 202 -> COMPLETED |
| MR-011 | Successful Data Governance intake | Bank 11 | 202 -> COMPLETED |
| MR-012 | Successful Modern Workplace intake | Bank 12 | 202 -> COMPLETED |
| MR-013 | Successful Payments Modernization intake | Bank 13 | 202 -> COMPLETED |
| MR-014 | Successful Insurance Operations intake | Bank 14 | 202 -> COMPLETED |
| MR-015 | Successful Healthcare Platform intake | Bank 15 | 202 -> COMPLETED |
| MR-016 | Duplicate replay of MR-001 | Bank 16 | 202 -> DUPLICATE |
| MR-017 | Empty Markdown input | Bank 17 | 202 -> FAILED |
| MR-018 | Unsupported CSV input | Bank 18 | 202 -> FAILED |
| MR-019 | Missing account | - | 400 |
| MR-020 | Missing source | Bank 20 | 400 |

## Assertions

### Successful records MR-001 through MR-015

- `POST /runs` returns HTTP `202`.
- The response contains a UUID `run_id` and status `STARTED`.
- Polling eventually returns `COMPLETED` when valid model credentials are configured.
- Receiver metadata identifies a Markdown input and no duplicate.
- Classification contains at least two requirements and a relevant category.
- Requirement ownership and questionnaire outputs are present.
- Generated wording can vary because the records exercise a model-backed workflow; assert schema, traceability, minimum counts, and relevant categories rather than exact prose.

### Duplicate record MR-016

- Execute only after MR-001.
- The request is accepted with HTTP `202`.
- Terminal status is `DUPLICATE`.
- `metadata.duplicate_of` references MR-001's run ID.
- The immutable first registration remains the only tracker row for that SHA-256.

### Failure records MR-017 and MR-018

- The request is accepted asynchronously with HTTP `202`.
- MR-017 terminates as `FAILED` because it has no extractable text.
- MR-018 terminates as `FAILED` because CSV is not a supported input type.

### Validation records MR-019 and MR-020

- Validation occurs before a background run is created.
- The API returns HTTP `400`.
- No `run_id` is returned.

## Reset guidance

Duplicate detection uses the configured Excel tracker. Use an isolated tracker for repeatable dataset runs, or archive the prior test tracker before rerunning MR-001 through MR-016.
