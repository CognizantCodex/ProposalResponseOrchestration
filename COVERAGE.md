# Unit-test coverage

Coverage is measured against the `orchestration` package with branch coverage enabled.

Run from the repository root:

```powershell
python -m coverage erase
python -m coverage run --branch -m unittest discover -s tests
python -m coverage report -m
```

Latest local run:

| Measure | Result |
| --- | ---: |
| Tests | 19 passed |
| Statements | 496 |
| Missed statements | 53 |
| Branch coverage | 64 branches, 13 partial |
| Total coverage | **88%** |

The suite covers successful orchestration, duplicate and immutable intake behavior, unsupported and empty files, GitHub URL intake, DOCX extraction, SLS knowledge fallbacks, model payload validation, retry exhaustion, tracker failure updates, state persistence, and HTTP request validation/status lookup.

