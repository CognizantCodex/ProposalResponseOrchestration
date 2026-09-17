from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import PipelineState


class StateStore:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir

    def save(self, state: PipelineState) -> Path:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        target = self.state_dir / f"{state.run_id}.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(target)
        return target

    def load(self, run_id: str) -> dict[str, Any] | None:
        target = self.state_dir / f"{run_id}.json"
        if not target.is_file():
            return None
        return json.loads(target.read_text(encoding="utf-8"))
