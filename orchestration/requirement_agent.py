from __future__ import annotations

from .llm import StructuredLlm
from .models import ClassificationResult, OwnershipAssignment, RequirementsResult

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["requirement_brief", "ownership_map", "evidence_gaps", "clarification_gaps"],
    "properties": {
        "requirement_brief": {"type": "string"},
        "evidence_gaps": {"type": "array", "items": {"type": "string"}},
        "clarification_gaps": {"type": "array", "items": {"type": "string"}},
        "ownership_map": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["requirement_id", "primary_service_line", "proposed_owner", "rationale", "confidence"],
            "properties": {
                "requirement_id": {"type": "string"}, "primary_service_line": {"type": "string"},
                "proposed_owner": {"type": "string"}, "rationale": {"type": "string"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            },
        }},
    },
}


class RequirementAgent:
    def __init__(self, llm: StructuredLlm):
        self.llm = llm

    def run(self, *, classification: ClassificationResult, sls_reference: str) -> RequirementsResult:
        classification_payload = classification.__dict__ | {"requirements": [item.__dict__ for item in classification.requirements]}
        result = self.llm.generate(
            schema_name="requirement_ownership",
            instructions="Create a concise requirement brief and map every requirement ID to the best available service line and owner. Use only the supplied SLS reference. If no qualified owner exists, use UNASSIGNED and low confidence. Never invent capabilities, people, evidence, or commitments.",
            payload={"classification": classification_payload, "sls_reference": sls_reference},
            schema=SCHEMA,
        )
        return RequirementsResult(result["requirement_brief"], [OwnershipAssignment(**item) for item in result["ownership_map"]], result["evidence_gaps"], result["clarification_gaps"])


