from __future__ import annotations

import json
from typing import Any, Protocol


class StructuredLlm(Protocol):
    def generate(self, *, schema_name: str, instructions: str, payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]: ...


class OpenAIJsonClient:
    """Responses API adapter using strict Structured Outputs."""

    def __init__(self, model: str):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def generate(self, *, schema_name: str, instructions: str, payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=json.dumps(payload, ensure_ascii=False),
            store=False,
            text={"format": {"type": "json_schema", "name": schema_name, "strict": True, "schema": schema}, "verbosity": "low"},
        )
        if not response.output_text:
            raise RuntimeError(f"OpenAI returned no structured output for {schema_name}")
        return json.loads(response.output_text)


