import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cluster.node_heartbeat import heartbeat_payload
from cluster.node_worker import NodeWorkerPool
from core.event_bus import EventBus
from core.event_types import EventTypes

BUS = EventBus()


ACTIVE_TASKS = 0
ACTIVE_LOCK = threading.Lock()
WORKER_POOL = NodeWorkerPool(max_workers=4)


def _inc_active(delta: int):
    global ACTIVE_TASKS
    with ACTIVE_LOCK:
        ACTIVE_TASKS += delta


def _get_active() -> int:
    with ACTIVE_LOCK:
        return ACTIVE_TASKS


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._json({"status": "ok", "active_tasks": _get_active()})
            return
        if self.path == "/heartbeat":
            payload = heartbeat_payload(active_tasks=_get_active())
            BUS.publish(EventTypes.NODE_HEARTBEAT, payload)
            self._json(payload)
            return
        self._json({"error": "not_found"}, status=404)

    def do_POST(self):
        if self.path != "/task":
            self._json({"error": "not_found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
            task = payload.get("task", "")
            _inc_active(1)
            fut = WORKER_POOL.submit_task(task)
            out = fut.result()
            _inc_active(-1)
            self._json(out)
        except Exception as e:
            _inc_active(-1)
            self._json({"error": str(e)}, status=500)


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Cluster Node Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
