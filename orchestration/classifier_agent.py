from __future__ import annotations

from .llm import StructuredLlm
from .models import ClassificationResult, Requirement

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["summary", "categories", "winning_themes", "requirements", "commercial_questions"],
    "properties": {
        "summary": {"type": "string"},
        "categories": {"type": "array", "items": {"type": "string"}},
        "winning_themes": {"type": "array", "items": {"type": "string"}},
        "commercial_questions": {"type": "array", "items": {"type": "string"}},
        "requirements": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["requirement_id", "title", "description", "mandatory", "source_hint", "category"],
            "properties": {
                "requirement_id": {"type": "string"}, "title": {"type": "string"},
                "description": {"type": "string"}, "mandatory": {"type": "boolean"},
                "source_hint": {"type": "string"}, "category": {"type": "string"},
            },
        }},
    },
}


class ClassifierAgent:
    def __init__(self, llm: StructuredLlm):
        self.llm = llm

    def run(self, *, account: str, document_text: str, category_reference: str) -> ClassificationResult:
        result = self.llm.generate(
            schema_name="rfp_classification",
            instructions="Extract every material RFP requirement. Preserve traceability with page, slide, section, or heading hints. Classify against supplied categories when possible. Mark mandatory only when the source says so. Winning themes must be evidence-backed, not unsupported claims.",
            payload={"account": account, "category_reference": category_reference, "rfp_text": document_text},
            schema=SCHEMA,
        )
        return ClassificationResult(result["summary"], result["categories"], result["winning_themes"], [Requirement(**item) for item in result["requirements"]], result["commercial_questions"])


