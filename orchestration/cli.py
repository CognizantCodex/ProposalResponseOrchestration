from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Settings
from .orchestrator import AgentOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RFP agent orchestration pipeline")
    parser.add_argument("--account", required=True, help="Account folder/name, for example WellsFargo")
    parser.add_argument("--file", required=True, type=Path, help="RFP path: PDF, DOCX, PPTX, TXT, or Markdown")
    args = parser.parse_args()
    state = AgentOrchestrator(Settings.from_env()).run(account=args.account, source_path=args.file)
    print(json.dumps(state.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


