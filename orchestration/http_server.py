from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from uuid import uuid4

from .config import Settings
from .orchestrator import AgentOrchestrator
from .state_store import StateStore


class Handler(BaseHTTPRequestHandler):
    settings = Settings.from_env()
    orchestrator = None
    store = StateStore(settings.state_dir)

    @classmethod
    def get_orchestrator(cls):
        if cls.orchestrator is None:
            cls.orchestrator = AgentOrchestrator(cls.settings)
        return cls.orchestrator

    def _json(self, status: int, body: dict) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/runs":
            self._json(404, {"error": "Not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length))
            account = str(payload["account"]).strip()
            source = payload.get("source_url") or payload.get("source_path")
            if not account or not source:
                raise ValueError("account and source_url/source_path are required")
            run_id = str(uuid4())
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return

        def execute():
            try:
                self.get_orchestrator().run(account=account, source_path=source, run_id=run_id)
            except Exception:
                # The state store contains the detailed failure event.
                pass

        Thread(target=execute, daemon=True).start()
        self._json(202, {"run_id": run_id, "status": "STARTED"})

    def do_GET(self):
        prefix = "/runs/"
        if not self.path.startswith(prefix):
            self._json(404, {"error": "Not found"})
            return
        run_id = self.path[len(prefix):].split("?", 1)[0]
        target = self.settings.state_dir / f"{run_id}.json"
        if not target.is_file():
            self._json(404, {"error": "Run not found"})
            return
        self._json(200, json.loads(target.read_text(encoding="utf-8")))

    def log_message(self, format, *args):
        return


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="HTTP event bridge for the RFP orchestrator")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"RFP orchestration API listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

