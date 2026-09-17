from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RfpMetadata:
    run_id: str
    account: str
    source_path: str
    file_name: str
    file_type: str
    file_size: int
    sha256: str
    unit_count: int
    word_count: int
    ingested_at: str
    duplicate_of: str | None = None


@dataclass
class Requirement:
    requirement_id: str
    title: str
    description: str
    mandatory: bool
    source_hint: str
    category: str


@dataclass
class ClassificationResult:
    summary: str
    categories: list[str]
    winning_themes: list[str]
    requirements: list[Requirement]
    commercial_questions: list[str]


@dataclass
class OwnershipAssignment:
    requirement_id: str
    primary_service_line: str
    proposed_owner: str
    rationale: str
    confidence: str


@dataclass
class RequirementsResult:
    requirement_brief: str
    ownership_map: list[OwnershipAssignment]
    evidence_gaps: list[str]
    clarification_gaps: list[str]


@dataclass
class OpenQuestion:
    question_id: str
    requirement_id: str
    question: str
    proposed_owner: str
    status: str = "OPEN"


@dataclass
class QuestionnaireResult:
    open_questions: list[OpenQuestion]
    response_summary: str


@dataclass
class PipelineState:
    run_id: str
    account: str
    source_path: str
    status: str = "CREATED"
    current_agent: str = "orchestrator"
    attempts: dict[str, int] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] | None = None
    classification: dict[str, Any] | None = None
    requirements: dict[str, Any] | None = None
    questionnaire: dict[str, Any] | None = None
    error: str | None = None

    def event(self, agent: str, status: str, message: str) -> None:
        self.current_agent = agent
        self.status = status
        self.events.append({"at": utc_now(), "agent": agent, "status": status, "message": message})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


