import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from monitor.metrics_collector import collect_metrics


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/system/metrics':
            self._json(collect_metrics())
            return
        self._json({'error': 'not_found'}, status=404)


def main():
    p = argparse.ArgumentParser(description='GrayWolf System Metrics endpoint')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8792)
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        print(json.dumps(collect_metrics(), ensure_ascii=False))
        return

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == '__main__':
    main()
