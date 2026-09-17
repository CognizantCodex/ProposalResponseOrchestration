from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from .api_dtos import ApiResponse, ErrorResponse
from .run_controller import RunController
from .run_service import RunService


class Handler(BaseHTTPRequestHandler):
    controller: RunController | None = None
    max_body_bytes = 1_000_000

    @classmethod
    def get_controller(cls) -> RunController:
        if cls.controller is None:
            cls.controller = RunController(RunService())
        return cls.controller

    def _json(self, response: ApiResponse) -> None:
        raw = json.dumps(response.body, ensure_ascii=False).encode("utf-8")
        self.send_response(response.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> object:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length must be an integer") from exc
        if length <= 0:
            raise ValueError("JSON request body is required")
        if length > self.max_body_bytes:
            raise ValueError("JSON request body exceeds 1000000 bytes")
        try:
            return json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must contain valid JSON") from exc

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/runs":
            self._json(self.get_controller().route_not_found())
            return
        try:
            payload = self._read_json()
        except ValueError as exc:
            self._json(ApiResponse(400, ErrorResponse(str(exc)).to_dict()))
            return
        self._json(self.get_controller().create_run(payload))

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        prefix = "/runs/"
        if not path.startswith(prefix) or not path[len(prefix):]:
            self._json(self.get_controller().route_not_found())
            return
        self._json(self.get_controller().get_run(path[len(prefix):]))

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="HTTP REST service for RFP orchestration")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    Handler.controller = RunController(RunService())
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"RFP orchestration API listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
