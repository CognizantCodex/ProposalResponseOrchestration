from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable, TypeVar
from uuid import uuid4

from .classifier_agent import ClassifierAgent
from .config import Settings
from .knowledge import DEFAULT_CATEGORIES, read_optional_text, read_sls_reference
from .llm import OpenAIJsonClient, StructuredLlm
from .models import PipelineState
from .questionnaire_agent import QuestionnaireAgent
from .receiver_agent import DuplicateRfpError, ReceiverAgent
from .requirement_agent import RequirementAgent
from .state_store import StateStore
from .tracker import ExcelTracker

T = TypeVar("T")


class AgentOrchestrator:
    def __init__(self, settings: Settings | None = None, llm: StructuredLlm | None = None):
        self.settings = settings or Settings.from_env()
        self.tracker = ExcelTracker(self.settings.tracker_path)
        self.store = StateStore(self.settings.state_dir)
        self.llm = llm or OpenAIJsonClient(self.settings.model)
        self.receiver = ReceiverAgent(self.tracker)
        self.classifier = ClassifierAgent(self.llm)
        self.requirement_agent = RequirementAgent(self.llm)
        self.questionnaire = QuestionnaireAgent(self.llm)

    def _run_with_retry(self, state: PipelineState, agent: str, action: Callable[[], T]) -> T:
        last_error: Exception | None = None
        for attempt in range(1, self.settings.max_agent_retries + 2):
            state.attempts[agent] = attempt
            state.event(agent, f"{agent.upper()}_RUNNING", f"Attempt {attempt}")
            self.store.save(state)
            try:
                return action()
            except Exception as exc:
                last_error = exc
                state.event(agent, f"{agent.upper()}_RETRY", str(exc))
                self.store.save(state)
                if attempt <= self.settings.max_agent_retries:
                    time.sleep(min(2 ** (attempt - 1), 4))
        assert last_error is not None
        raise last_error

    def run(self, *, account: str, source_path: Path | str, run_id: str | None = None) -> PipelineState:
        run_id = run_id or str(uuid4())
        state = PipelineState(run_id=run_id, account=account, source_path=str(source_path))
        state.event("orchestrator", "STARTED", "Pipeline created")
        self.store.save(state)
        try:
            metadata, text = self.receiver.run(run_id=run_id, account=account, source_path=source_path)
            state.metadata = asdict(metadata)
            state.event("receiver", "VALIDATED", "File and duplicate validation passed")
            self.store.save(state)

            category_reference = read_optional_text(self.settings.category_path, DEFAULT_CATEGORIES)
            classification = self._run_with_retry(state, "classifier", lambda: self.classifier.run(account=account, document_text=text, category_reference=category_reference))
            state.classification = asdict(classification)
            state.event("classifier", "CLASSIFIED", f"Extracted {len(classification.requirements)} requirements")
            self.store.save(state)

            sls_reference = read_sls_reference(self.settings.sls_contact_path, self.settings.employee_master_path)
            requirements = self._run_with_retry(state, "requirement", lambda: self.requirement_agent.run(classification=classification, sls_reference=sls_reference))
            state.requirements = asdict(requirements)
            state.event("requirement", "OWNERS_MAPPED", f"Mapped {len(requirements.ownership_map)} requirements")
            self.store.save(state)

            questionnaire = self._run_with_retry(state, "questionnaire", lambda: self.questionnaire.run(classification=classification, requirements=requirements))
            state.questionnaire = asdict(questionnaire)
            state.event("questionnaire", "QUESTIONNAIRE_READY", f"Created {len(questionnaire.open_questions)} open questions")
            state.event("orchestrator", "COMPLETED", "All agents completed")
            self.tracker.update(run_id, status="COMPLETED", agent="orchestrator")
            self.store.save(state)
            return state
        except DuplicateRfpError as exc:
            state.metadata = asdict(exc.metadata)
            state.error = str(exc)
            state.event("receiver", "DUPLICATE", str(exc))
            self.store.save(state)
            return state
        except Exception as exc:
            state.error = str(exc)
            state.event(state.current_agent, "FAILED", str(exc))
            self.tracker.update(run_id, status="FAILED", agent=state.current_agent, error=str(exc))
            self.store.save(state)
            raise

