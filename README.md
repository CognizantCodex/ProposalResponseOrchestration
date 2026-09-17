# Proposal Response Orchestration

React/Vite UI and Python agent orchestration for turning customer RFPs into traceable requirements, ownership recommendations, evidence gaps, and managed questions.

## Source architecture

The REST implementation uses explicit layers:

- DTOs: `orchestration/api_dtos.py`
- Controller: `orchestration/run_controller.py`
- Service: `orchestration/run_service.py`
- HTTP transport: `orchestration/http_server.py`
- Domain orchestration: `orchestration/orchestrator.py`

See [ARCHITECTURE.md](ARCHITECTURE.md) for the before/after diagram and request flow.

## Getting started

Implementation and usage guidance is available in [orchestration/README.md](orchestration/README.md) and [Dashboard/README.md](Dashboard/README.md).

Run the API-layer and orchestration tests:

```powershell
python -m unittest discover -s tests -v
```

## Sample endpoint dataset

The [sample-data package](sample-data/README.md) provides 20 mock REST endpoint records, synthetic RFP inputs, and documented expected outcomes for successful, duplicate, extraction-failure, unsupported-format, and request-validation scenarios.
