#!/usr/bin/env python3
"""Graywolf Runtime Kernel Entry (v2 Job 1).

Single entry for lifecycle operations:
- run-once
- start
- stop
- status
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from core.approval import ApprovalManager
from core.command_bus import CommandBus
from core.session_state import SessionStateStore
from monitor.approval_health import get_approval_callback_summary, get_replan_stats

ROOT = Path("/home/adem/graywolf")
PY = Path("/home/adem/.openclaw/workspace/.venv/bin/python")
WORKER = ROOT / "scripts" / "run_autonomy_worker.py"
DAEMON = ROOT / "scripts" / "autonomy_daemon.sh"
SESSION_STORE = SessionStateStore(root=str(ROOT / "sessions"))


def _exec(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "cmd": " ".join(cmd),
        "exit_code": p.returncode,
        "stdout": (p.stdout or "").strip(),
        "stderr": (p.stderr or "").strip(),
    }


def run_once(session_id: str) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    p = subprocess.run([str(PY), str(WORKER)], capture_output=True, text=True, check=False, env=env)
    parsed = None
    raw = (p.stdout or "").strip().splitlines()
    if raw:
        try:
            parsed = json.loads(raw[-1])
        except Exception:
            parsed = {"raw": raw[-1]}
    out = {
        "status": "ok" if p.returncode == 0 else "error",
        "worker_exit_code": p.returncode,
        "worker": parsed,
        "stderr": (p.stderr or "").strip(),
    }
    worker_result = (parsed or {}).get("result", {}) if isinstance(parsed, dict) else {}
    task_id = worker_result.get("task_id") if isinstance(worker_result, dict) else None
    SESSION_STORE.record(
        session_id,
        command={"action": "run-once"},
        result=out,
        error=out.get("stderr") or None,
        active_task=task_id,
    )
    return out


def daemon(action: str, session_id: str) -> dict:
    r = _exec(["bash", str(DAEMON), action])
    out = {
        "status": "ok" if r["exit_code"] == 0 else "error",
        "action": action,
        "result": r,
    }
    SESSION_STORE.record(
        session_id,
        command={"action": action},
        result=out,
        error=r.get("stderr") or None,
    )
    return out


def status(session_id: str) -> dict:
    daemon_status = daemon("status", session_id)

    approval_manager = ApprovalManager()
    pending_runtime = len(approval_manager.pending_requests())

    try:
        replan = get_replan_stats()
    except Exception as e:
        replan = {"status": "degraded", "error": str(e)}

    try:
        callbacks = get_approval_callback_summary()
    except Exception as e:
        callbacks = {"status": "degraded", "error": str(e)}

    session = SESSION_STORE.load(session_id)
    SESSION_STORE.record(session_id, command={"action": "status"}, result={"status": "ok"})

    return {
        "status": "ok",
        "runtime": "graywolf-runtime-kernel-v1",
        "canonical": {
            "loop": "core/autonomous_loop.py",
            "worker": "scripts/run_autonomy_worker.py",
            "daemon": "scripts/autonomy_daemon.sh",
            "orchestrator": "core/orchestrator.py",
            "workflow": "workflows/runner.py",
        },
        "daemon": daemon_status,
        "approval": {
            "pending_runtime_requests": pending_runtime,
            "replan_health": replan,
            "callbacks": callbacks,
        },
        "session": {
            "session_id": session.get("session_id"),
            "created_at": session.get("created_at"),
            "updated_at": session.get("updated_at"),
            "last_command": session.get("last_command"),
            "last_result": session.get("last_result"),
            "last_error": session.get("last_error"),
            "active_task": session.get("active_task"),
            "history_count": session.get("history_count"),
            "restored": True,
        },
    }


def submit_command(intent: str, payload_text: str, source: str, session_id: str) -> dict:
    try:
        payload = json.loads(payload_text) if payload_text else {}
    except Exception as e:
        out = {
            "status": "error",
            "artifacts": {},
            "errors": [f"invalid_payload_json: {e}"],
        }
        SESSION_STORE.record(session_id, command={"action": "submit-command", "intent": intent}, result=out, error=str(e))
        return out

    bus = CommandBus(
        queue_dir=str(ROOT / "tasks" / "queue"),
        processed_dir=str(ROOT / "tasks" / "processed"),
    )
    envelope = bus.build_envelope(intent=intent, payload=payload, source=source)
    out = bus.submit(envelope)
    task_id = ((out.get("task") or {}).get("task_id")) if isinstance(out, dict) else None
    SESSION_STORE.record(
        session_id,
        command={"action": "submit-command", "intent": intent, "source": source, "payload": payload},
        result=out,
        active_task=task_id,
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Graywolf Runtime Kernel")
    ap.add_argument("action", choices=["run-once", "start", "stop", "status", "submit-command"], help="Runtime action")
    ap.add_argument("--intent", default="")
    ap.add_argument("--payload", default="{}", help="JSON payload for submit-command")
    ap.add_argument("--source", default="cli")
    ap.add_argument("--session-id", default="default", help="Runtime session id")
    args = ap.parse_args()

    if args.action == "run-once":
        out = run_once(args.session_id)
    elif args.action == "start":
        out = daemon("start", args.session_id)
    elif args.action == "stop":
        out = daemon("stop", args.session_id)
    elif args.action == "submit-command":
        if not args.intent:
            out = {"status": "error", "artifacts": {}, "errors": ["intent_required"]}
            SESSION_STORE.record(args.session_id, command={"action": "submit-command"}, result=out, error="intent_required")
        else:
            out = submit_command(args.intent, args.payload, args.source, args.session_id)
    else:
        out = status(args.session_id)

    payload = {"ts": datetime.now().isoformat(), **out}
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if out.get("status") in {"ok", "queued"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
