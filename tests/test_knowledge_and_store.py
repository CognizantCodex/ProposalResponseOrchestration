import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from openpyxl import Workbook

from orchestration.knowledge import read_optional_text, read_sls_reference
from orchestration.models import PipelineState
from orchestration.state_store import StateStore


class KnowledgeAndStoreTest(TestCase):
    def test_knowledge_fallbacks_and_markdown(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIn("Application modernization", read_optional_text(root / "missing.md", "Application modernization"))
            contact = root / "contacts.md"
            contact.write_text("SEG | owner@example.com", encoding="utf-8")
            self.assertIn("owner@example.com", read_sls_reference(contact, root / "missing.xlsx"))

    def test_employee_workbook_is_read_when_markdown_is_missing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            workbook = Workbook()
            sheet = workbook.active
            sheet.append(["Service Line", "Email"])
            sheet.append(["CIS", "cis@example.com"])
            workbook.save(root / "employees.xlsx")
            reference = read_sls_reference(root / "missing.md", root / "employees.xlsx")
            self.assertIn("cis@example.com", reference)

    def test_state_store_replaces_json_atomically(self):
        with TemporaryDirectory() as tmp:
            state = PipelineState(run_id="run-1", account="JPMC", source_path="input.md")
            state.event("receiver", "VALIDATED", "ok")
            target = StateStore(Path(tmp)).save(state)
            self.assertEqual("VALIDATED", json.loads(target.read_text(encoding="utf-8"))["status"])

