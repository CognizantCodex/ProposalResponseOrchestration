from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse


class RequestValidationError(ValueError):
    """Raised when an API payload does not satisfy the public contract."""


@dataclass(frozen=True)
class CreateRunRequest:
    account: str
    source: str
    source_field: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "CreateRunRequest":
        if not isinstance(payload, Mapping):
            raise RequestValidationError("JSON body must be an object")

        allowed = {"account", "source_url", "source_path"}
        unknown = sorted(set(payload) - allowed)
        if unknown:
            raise RequestValidationError(f"Unsupported field(s): {', '.join(unknown)}")

        account = payload.get("account")
        source_url = payload.get("source_url")
        source_path = payload.get("source_path")

        if not isinstance(account, str) or not account.strip():
            raise RequestValidationError("account and source_url/source_path are required")

        supplied_sources = [
            (name, value.strip())
            for name, value in (("source_url", source_url), ("source_path", source_path))
            if isinstance(value, str) and value.strip()
        ]
        non_string_source = any(
            value is not None and not isinstance(value, str)
            for value in (source_url, source_path)
        )
        if non_string_source or not supplied_sources:
            raise RequestValidationError("account and source_url/source_path are required")
        if len(supplied_sources) != 1:
            raise RequestValidationError("Provide exactly one of source_url or source_path")

        source_field, source = supplied_sources[0]
        if source_field == "source_url":
            parsed = urlparse(source)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise RequestValidationError("source_url must be an absolute HTTP or HTTPS URL")

        return cls(account=account.strip(), source=source, source_field=source_field)


@dataclass(frozen=True)
class RunAcceptedResponse:
    run_id: str
    status: str = "STARTED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ErrorResponse:
    error: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    body: dict[str, Any]
