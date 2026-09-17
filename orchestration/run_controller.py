from __future__ import annotations

from uuid import UUID

from .api_dtos import ApiResponse, CreateRunRequest, ErrorResponse, RequestValidationError
from .run_service import RunService


class RunController:
    """HTTP-independent controller for the public run API."""

    def __init__(self, service: RunService):
        self.service = service

    def create_run(self, payload: object) -> ApiResponse:
        try:
            request = CreateRunRequest.from_payload(payload)
        except RequestValidationError as exc:
            return ApiResponse(400, ErrorResponse(str(exc)).to_dict())

        accepted = self.service.start_run(request)
        return ApiResponse(202, accepted.to_dict())

    def get_run(self, run_id: str) -> ApiResponse:
        try:
            normalized = str(UUID(run_id))
        except (ValueError, AttributeError):
            return ApiResponse(400, ErrorResponse("run_id must be a UUID").to_dict())

        state = self.service.get_run(normalized)
        if state is None:
            return ApiResponse(404, ErrorResponse("Run not found").to_dict())
        return ApiResponse(200, state)

    @staticmethod
    def route_not_found() -> ApiResponse:
        return ApiResponse(404, ErrorResponse("Not found").to_dict())
