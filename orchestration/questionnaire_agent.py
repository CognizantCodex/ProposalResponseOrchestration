from __future__ import annotations

from .llm import StructuredLlm
from .models import ClassificationResult, OpenQuestion, QuestionnaireResult, RequirementsResult

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["open_questions", "response_summary"],
    "properties": {
        "response_summary": {"type": "string"},
        "open_questions": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["question_id", "requirement_id", "question", "proposed_owner", "status"],
            "properties": {
                "question_id": {"type": "string"}, "requirement_id": {"type": "string"},
                "question": {"type": "string"}, "proposed_owner": {"type": "string"},
                "status": {"type": "string", "enum": ["OPEN", "ANSWERED", "BLOCKED"]},
            },
        }},
    },
}


class QuestionnaireAgent:
    def __init__(self, llm: StructuredLlm):
        self.llm = llm

    def run(self, *, classification: ClassificationResult, requirements: RequirementsResult) -> QuestionnaireResult:
        classification_payload = classification.__dict__ | {"requirements": [item.__dict__ for item in classification.requirements]}
        requirements_payload = requirements.__dict__ | {"ownership_map": [item.__dict__ for item in requirements.ownership_map]}
        result = self.llm.generate(
            schema_name="rfp_questionnaire",
            instructions="Create only questions needed to resolve ambiguity, missing evidence, ownership, dependencies, commercial terms, or unsupported claims. Link each question to a requirement ID when possible, use an owner from the map, and keep new questions OPEN.",
            payload={"classification": classification_payload, "requirements": requirements_payload},
            schema=SCHEMA,
        )
        return QuestionnaireResult([OpenQuestion(**item) for item in result["open_questions"]], result["response_summary"])


