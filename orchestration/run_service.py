from __future__ import annotations

from collections.abc import Callable
from threading import Lock, Thread
from typing import Any, Protocol
from uuid import uuid4

from .api_dtos import CreateRunRequest, RunAcceptedResponse
from .config import Settings
from .models import PipelineState
from .orchestrator import AgentOrchestrator
from .state_store import StateStore


class Orchestrator(Protocol):
    def run(self, *, account: str, source_path: str, run_id: str | None = None) -> PipelineState: ...


Launcher = Callable[[Callable[[], None]], None]


def launch_in_background(action: Callable[[], None]) -> None:
    Thread(target=action, daemon=True).start()


class RunService:
    """Application service for run creation, execution, and status retrieval."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        orchestrator: Orchestrator | None = None,
        store: StateStore | None = None,
        launcher: Launcher | None = None,
    ):
        self.settings = settings or Settings.from_env()
        self.store = store or StateStore(self.settings.state_dir)
        self._orchestrator = orchestrator
        self._orchestrator_lock = Lock()
        self._launcher = launcher or launch_in_background

    def _get_orchestrator(self) -> Orchestrator:
        if self._orchestrator is None:
            with self._orchestrator_lock:
                if self._orchestrator is None:
                    self._orchestrator = AgentOrchestrator(self.settings)
        return self._orchestrator

    def start_run(self, request: CreateRunRequest) -> RunAcceptedResponse:
        run_id = str(uuid4())
        accepted = PipelineState(
            run_id=run_id,
            account=request.account,
            source_path=request.source,
        )
        accepted.event("service", "STARTED", "Run accepted by REST API")
        self.store.save(accepted)

        def execute() -> None:
            try:
                self._get_orchestrator().run(
                    account=request.account,
                    source_path=request.source,
                    run_id=run_id,
                )
            except Exception as exc:
                existing = self.store.load(run_id)
                if existing and existing.get("status") in {"COMPLETED", "DUPLICATE", "FAILED"}:
                    return
                failed = PipelineState(
                    run_id=run_id,
                    account=request.account,
                    source_path=request.source,
                    error=str(exc),
                )
                failed.event("service", "FAILED", str(exc))
                self.store.save(failed)

        self._launcher(execute)
        return RunAcceptedResponse(run_id=run_id)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self.store.load(run_id)
