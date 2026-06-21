from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockMealieHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/app/about":
            body = json.dumps({"version": "mock", "production": False}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9000), MockMealieHandler)
    server.serve_forever()
