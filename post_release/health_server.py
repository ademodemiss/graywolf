import argparse
import json
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

BIND = '127.0.0.1'
PORT = 8899


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/health':
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({'status': 'ok'}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


def run_server():
    srv = HTTPServer((BIND, PORT), HealthHandler)
    srv.serve_forever()


def self_test() -> dict:
    srv = HTTPServer((BIND, PORT), HealthHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f'http://{BIND}:{PORT}/health', timeout=3) as resp:
            raw = resp.read().decode('utf-8')
            ok = resp.status == 200 and 'ok' in raw
            return {'status': 'ok' if ok else 'failed', 'bind': BIND, 'port': PORT, 'http_status': resp.status}
    finally:
        srv.shutdown()
        srv.server_close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False))
    else:
        run_server()
