import json
import threading
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from orchestration.config import Settings
from orchestration.http_server import Handler
from orchestration.state_store import StateStore


class FakeOrchestrator:
    def __init__(self):
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)


class HttpServerTest(TestCase):
    def test_endpoint_validation_and_run_status_lookup(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            class TestHandler(Handler):
                settings = Settings(state_dir=root / "runs")
                orchestrator = FakeOrchestrator()
                store = StateStore(settings.state_dir)

            from http.server import ThreadingHTTPServer
            server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                request = Request(base + "/runs", data=b"{}", method="POST", headers={"Content-Type": "application/json"})
                with self.assertRaises(HTTPError) as missing:
                    urlopen(request)
                self.assertEqual(400, missing.exception.code)

                request = Request(base + "/runs", data=json.dumps({"account": "Bank 1", "source_url": "https://github.com/example/rfp.docx"}).encode(), method="POST", headers={"Content-Type": "application/json"})
                with urlopen(request) as response:
                    body = json.loads(response.read())
                self.assertEqual(202, response.status)
                self.assertEqual("STARTED", body["status"])
                self.assertEqual("Bank 1", TestHandler.orchestrator.calls[0]["account"])

                with self.assertRaises(HTTPError) as unknown:
                    urlopen(base + "/runs/unknown")
                self.assertEqual(404, unknown.exception.code)
            finally:
                server.shutdown()
                thread.join(timeout=2)
                server.server_close()

