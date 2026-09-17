from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import UUID, uuid4

from orchestration.api_dtos import CreateRunRequest, RequestValidationError
from orchestration.models import PipelineState
from orchestration.run_controller import RunController
from orchestration.run_service import RunService
from orchestration.state_store import StateStore


class FakeOrchestrator:
    def __init__(self, store: StateStore):
        self.store = store
        self.calls = []

    def run(self, *, account, source_path, run_id=None):
        self.calls.append((account, source_path, run_id))
        state = PipelineState(run_id=run_id, account=account, source_path=str(source_path))
        state.event("orchestrator", "COMPLETED", "Fake orchestration completed")
        self.store.save(state)
        return state


def run_now(action):
    action()


class ApiDtoTest(unittest.TestCase):
    def test_valid_source_url_is_normalized(self):
        request = CreateRunRequest.from_payload(
            {"account": " Bank 1 ", "source_url": "https://example.test/rfp.md"}
        )
        self.assertEqual("Bank 1", request.account)
        self.assertEqual("source_url", request.source_field)

    def test_missing_required_fields_are_rejected(self):
        for payload in ({}, {"account": "Bank 1"}, {"source_url": "https://example.test/rfp.md"}):
            with self.subTest(payload=payload):
                with self.assertRaises(RequestValidationError):
                    CreateRunRequest.from_payload(payload)

    def test_ambiguous_or_invalid_sources_are_rejected(self):
        invalid = [
            {"account": "Bank 1", "source_url": "ftp://example.test/rfp.md"},
            {
                "account": "Bank 1",
                "source_url": "https://example.test/rfp.md",
                "source_path": "sample.md",
            },
            {"account": "Bank 1", "source_path": 123},
            {"account": "Bank 1", "source_path": "sample.md", "extra": True},
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                with self.assertRaises(RequestValidationError):
                    CreateRunRequest.from_payload(payload)


class RunControllerTest(unittest.TestCase):
    def test_controller_creates_and_retrieves_a_run(self):
        with TemporaryDirectory() as temporary:
            store = StateStore(Path(temporary))
            orchestrator = FakeOrchestrator(store)
            service = RunService(
                store=store,
                orchestrator=orchestrator,
                launcher=run_now,
            )
            controller = RunController(service)

            created = controller.create_run(
                {"account": "Bank 1", "source_path": "sample.md"}
            )
            self.assertEqual(202, created.status_code)
            UUID(created.body["run_id"])
            self.assertEqual("STARTED", created.body["status"])

            fetched = controller.get_run(created.body["run_id"])
            self.assertEqual(200, fetched.status_code)
            self.assertEqual("COMPLETED", fetched.body["status"])
            self.assertEqual(
                [("Bank 1", "sample.md", created.body["run_id"])],
                orchestrator.calls,
            )

    def test_controller_returns_validation_errors(self):
        service = RunService(launcher=run_now)
        controller = RunController(service)

        response = controller.create_run({"account": "", "source_path": "sample.md"})
        self.assertEqual(400, response.status_code)
        self.assertIn("required", response.body["error"])

        response = controller.get_run("not-a-uuid")
        self.assertEqual(400, response.status_code)
        self.assertIn("UUID", response.body["error"])

    def test_controller_returns_not_found_for_unknown_run(self):
        with TemporaryDirectory() as temporary:
            controller = RunController(
                RunService(store=StateStore(Path(temporary)), launcher=run_now)
            )
            response = controller.get_run(str(uuid4()))
            self.assertEqual(404, response.status_code)
            self.assertEqual("Run not found", response.body["error"])


if __name__ == "__main__":
    unittest.main()
