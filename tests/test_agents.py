from unittest import TestCase

from orchestration.classifier_agent import ClassifierAgent
from orchestration.models import ClassificationResult, OwnershipAssignment, RequirementsResult, Requirement
from orchestration.questionnaire_agent import QuestionnaireAgent
from orchestration.requirement_agent import RequirementAgent


class AgentLlm:
    def __init__(self):
        self.calls = []

    def generate(self, *, schema_name, instructions, payload, schema):
        self.calls.append((schema_name, payload))
        if schema_name == "rfp_classification":
            return {"summary": "Java migration", "categories": ["Application modernization"], "winning_themes": ["Phased migration"], "requirements": [{"requirement_id": "R1", "title": "Migration plan", "description": "Provide a phased plan", "mandatory": True, "source_hint": "Section 2", "category": "Application modernization"}], "commercial_questions": ["What is the target timeline?"]}
        if schema_name == "requirement_ownership":
            return {"requirement_brief": "One mandatory requirement.", "ownership_map": [{"requirement_id": "R1", "primary_service_line": "SEG", "proposed_owner": "UNASSIGNED", "rationale": "No named owner in reference", "confidence": "low"}], "evidence_gaps": ["Named architect"], "clarification_gaps": []}
        return {"open_questions": [{"question_id": "Q1", "requirement_id": "R1", "question": "Which Java workloads are in scope?", "proposed_owner": "UNASSIGNED", "status": "OPEN"}], "response_summary": "One scope question."}


class AgentTest(TestCase):
    def setUp(self):
        self.llm = AgentLlm()
        self.classification = ClassifierAgent(self.llm).run(account="Bank 1", document_text="migrate Java", category_reference="Application modernization")
        self.requirements = RequirementAgent(self.llm).run(classification=self.classification, sls_reference="SEG | UNASSIGNED")

    def test_classifier_preserves_traceability_and_categories(self):
        self.assertIsInstance(self.classification, ClassificationResult)
        self.assertEqual("Application modernization", self.classification.categories[0])
        self.assertTrue(self.classification.requirements[0].mandatory)
        self.assertEqual("Section 2", self.classification.requirements[0].source_hint)

    def test_requirement_agent_allows_unassigned_owner_and_records_gap(self):
        self.assertIsInstance(self.requirements, RequirementsResult)
        self.assertEqual("UNASSIGNED", self.requirements.ownership_map[0].proposed_owner)
        self.assertEqual(["Named architect"], self.requirements.evidence_gaps)

    def test_questionnaire_links_open_question_to_requirement(self):
        result = QuestionnaireAgent(self.llm).run(classification=self.classification, requirements=self.requirements)
        self.assertEqual("OPEN", result.open_questions[0].status)
        self.assertEqual("R1", result.open_questions[0].requirement_id)

    def test_invalid_classifier_payload_fails_loudly(self):
        class Broken:
            def generate(self, **kwargs):
                return {"summary": "missing required fields"}
        with self.assertRaises(KeyError):
            ClassifierAgent(Broken()).run(account="Bank 1", document_text="text", category_reference="categories")

