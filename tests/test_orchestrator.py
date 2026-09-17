from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from orchestration.config import Settings
from orchestration.orchestrator import AgentOrchestrator


class FakeLlm:
    def generate(self, *, schema_name, instructions, payload, schema):
        if schema_name == "rfp_classification":
            return {"summary": "Cloud request", "categories": ["Cloud migration"], "winning_themes": ["Traceable plan"], "requirements": [{"requirement_id": "REQ-001", "title": "Migration plan", "description": "Provide a plan", "mandatory": True, "source_hint": "Requirements", "category": "Cloud migration"}], "commercial_questions": []}
        if schema_name == "requirement_ownership":
            return {"requirement_brief": "One requirement.", "ownership_map": [{"requirement_id": "REQ-001", "primary_service_line": "CIS", "proposed_owner": "Cloud Architect", "rationale": "Cloud scope", "confidence": "high"}], "evidence_gaps": [], "clarification_gaps": []}
        return {"open_questions": [{"question_id": "Q-001", "requirement_id": "REQ-001", "question": "Which workloads?", "proposed_owner": "Cloud Architect", "status": "OPEN"}], "response_summary": "One question."}


class OrchestratorTest(unittest.TestCase):
    def test_pipeline_and_duplicate(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "sample.md"
            source.write_text("Provide a phased cloud migration plan.", encoding="utf-8")
            settings = Settings(tracker_path=root / "tracker.xlsx", state_dir=root / "runs", category_path=root / "category.md", sls_contact_path=root / "contacts.md", employee_master_path=root / "employees.xlsx", max_agent_retries=0)
            orchestrator = AgentOrchestrator(settings, llm=FakeLlm())
            completed = orchestrator.run(account="WellsFargo", source_path=source)
            self.assertEqual("COMPLETED", completed.status)
            duplicate = orchestrator.run(account="WellsFargo", source_path=source)
            self.assertEqual("DUPLICATE", duplicate.status)
            self.assertIsNotNone(duplicate.metadata["duplicate_of"])


if __name__ == "__main__":
    unittest.main()

