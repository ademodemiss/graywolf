import argparse
import json
from pathlib import Path
import sys

try:
    from dashboard.data import build_status_payload
    from dashboard.views import index_context
    from adapters.interface.api_adapter import submit_api_command
except ModuleNotFoundError:
    # Allow direct execution: python dashboard/server.py
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from dashboard.data import build_status_payload
    from dashboard.views import index_context
    from adapters.interface.api_adapter import submit_api_command


def run_test_mode() -> int:
    payload = build_status_payload()
    required = {"agent_status", "idle", "idle_minutes", "last_log_ts", "errors_24h", "last_logs", "last_workflows", "replan_bridge", "replan_bridge_entries", "replan_bridge_processing", "learning_recovery"}
    if not required.issubset(set(payload.keys())):
        print("dashboard_test_failed")
        return 1
    print("dashboard_test_ok")
    print(json.dumps(payload, ensure_ascii=False)[:500])
    return 0


def create_app():
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates

    app = FastAPI(title="GrayWolf Dashboard")
    templates = Jinja2Templates(directory="/home/adem/graywolf/dashboard/templates")
    app.mount("/static", StaticFiles(directory="/home/adem/graywolf/dashboard/static"), name="static")

    @app.get("/")
    def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request, **index_context()})

    @app.get("/api/status")
    def api_status():
        return JSONResponse(build_status_payload())

    @app.post("/api/command")
    async def api_command(request: Request):
        body = await request.json()
        intent = str(body.get("intent") or "").strip()
        payload = body.get("payload") or {}
        source = str(body.get("source") or "api")
        if not intent:
            return JSONResponse({"status": "error", "artifacts": {}, "errors": ["intent_required"]}, status_code=400)
        out = submit_api_command(intent=intent, payload=payload, source=source)
        code = 200 if out.get("status") in {"queued", "ok"} else 400
        return JSONResponse(out, status_code=code)

    return app


def main():
    parser = argparse.ArgumentParser(description="GrayWolf dashboard server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        raise SystemExit(run_test_mode())

    app = create_app()
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
