from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    rfp_root: Path = Path("RFP")
    customer_rfp_root: Path = Path("Customer RFP Documentation")
    tracker_path: Path = Path("data/RFP_Status_Tracker.xlsx")
    state_dir: Path = Path("data/runs")
    category_path: Path = Path("knowledge/category.md")
    sls_contact_path: Path = Path("knowledge/SLS point of contact.md")
    employee_master_path: Path = Path("knowledge/Synthetic_Service_Line_Employee_Master.xlsx")
    model: str = "gpt-5.5"
    max_agent_retries: int = 2

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            rfp_root=Path(os.getenv("RFP_ROOT", "RFP")),
            customer_rfp_root=Path(os.getenv("CUSTOMER_RFP_ROOT", "Customer RFP Documentation")),
            tracker_path=Path(os.getenv("RFP_TRACKER_PATH", "data/RFP_Status_Tracker.xlsx")),
            state_dir=Path(os.getenv("RFP_STATE_DIR", "data/runs")),
            category_path=Path(os.getenv("CATEGORY_PATH", "knowledge/category.md")),
            sls_contact_path=Path(os.getenv("SLS_CONTACT_PATH", "knowledge/SLS point of contact.md")),
            employee_master_path=Path(os.getenv("SLS_EMPLOYEE_MASTER_PATH", "knowledge/Synthetic_Service_Line_Employee_Master.xlsx")),
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
            max_agent_retries=int(os.getenv("MAX_AGENT_RETRIES", "2")),
        )

