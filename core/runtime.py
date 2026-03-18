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
import glob
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from core.approval import ApprovalManager
from core.command_bus import CommandBus
from core.session_state import SessionStateStore
from core.task_queue import TaskQueue
from monitor.approval_callback_router import ApprovalCallbackRouter
from monitor.approval_health import get_approval_callback_summary, get_replan_stats

ROOT = Path(os.environ.get("GRAYWOLF_ROOT", Path(__file__).resolve().parents[1]))
_DEFAULT_PY = Path.home() / ".openclaw" / "workspace" / ".venv" / "bin" / "python"
_REPO_PY = ROOT / ".venv" / "bin" / "python"
if _DEFAULT_PY.exists():
    PY = _DEFAULT_PY
elif _REPO_PY.exists():
    PY = _REPO_PY
else:
    PY = Path("python3")
WORKER = ROOT / "scripts" / "run_autonomy_worker.py"
DAEMON = ROOT / "scripts" / "autonomy_daemon.sh"
SESSION_STORE = SessionStateStore(root=str(ROOT / "sessions"))
QUEUE_DIR = ROOT / "tasks" / "queue"
PROCESSED_DIR = ROOT / "tasks" / "processed"
PENDING_APPROVALS_FILE = ROOT / "sessions" / "pending_approvals.json"


def _exec(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "cmd": " ".join(cmd),
        "exit_code": p.returncode,
        "stdout": (p.stdout or "").strip(),
        "stderr": (p.stderr or "").strip(),
    }


def _load_pending_approvals() -> dict:
    if not PENDING_APPROVALS_FILE.exists():
        return {}
    try:
        return json.loads(PENDING_APPROVALS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_pending_approvals(data: dict) -> None:
    PENDING_APPROVALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_APPROVALS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def _tail_task_summaries(dir_path: Path, limit: int = 5) -> list[dict]:
    files = sorted(glob.glob(str(dir_path / "*.json")))[-limit:]
    items: list[dict] = []
    for fp in files:
        try:
            d = json.loads(Path(fp).read_text(encoding="utf-8"))
        except Exception:
            continue
        items.append({
            "file": Path(fp).name,
            "task_id": d.get("task_id"),
            "status": d.get("status"),
            "intent": d.get("intent"),
            "source": d.get("source"),
            "queued_at": d.get("queued_at"),
            "processed_at": d.get("processed_at"),
        })
    return items


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

    queue_files = glob.glob(str(QUEUE_DIR / "*.json"))
    processed_files = glob.glob(str(PROCESSED_DIR / "*.json"))

    pending_map = _load_pending_approvals()
    pending_only = {k: v for k, v in pending_map.items() if (v or {}).get("status") == "pending"}

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
            "pending_command_approvals": len(pending_only),
            "pending_request_ids": sorted(list(pending_only.keys()))[-5:],
            "replan_health": replan,
            "callbacks": callbacks,
        },
        "queue": {
            "queue_depth": len(queue_files),
            "processed_count": len(processed_files),
            "last_5_queued": _tail_task_summaries(QUEUE_DIR, limit=5),
            "last_5_processed": _tail_task_summaries(PROCESSED_DIR, limit=5),
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

    if out.get("status") == "confirm_required":
        request_id = f"APR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        pending = _load_pending_approvals()
        pending[request_id] = {
            "session_id": session_id,
            "envelope": envelope,
            "created_at": datetime.now().isoformat(),
            "policy": out.get("policy") or {},
            "status": "pending",
        }
        _save_pending_approvals(pending)
        out["approval_request"] = {
            "request_id": request_id,
            "status": "pending",
        }

    task_id = ((out.get("task") or {}).get("task_id")) if isinstance(out, dict) else None
    SESSION_STORE.record(
        session_id,
        command={"action": "submit-command", "intent": intent, "source": source, "payload": payload},
        result=out,
        active_task=task_id,
    )
    return out


def handle_approval_callback(callback_data: str, actor: str = "runtime") -> dict:
    router = ApprovalCallbackRouter()
    try:
        cb = router.handle_callback(callback_data, actor=actor, metadata={"source": "runtime"})
    except Exception as e:
        return {"status": "error", "errors": [f"invalid_callback: {e}"], "artifacts": {}}

    parts = callback_data.split(":", 1)
    request_id = parts[1] if len(parts) == 2 else ""
    action = parts[0] if parts else ""

    pending = _load_pending_approvals()
    item = pending.get(request_id)
    if not item:
        return {"status": "error", "errors": ["pending_request_not_found"], "callback": cb, "artifacts": {}}

    if action == "approval.grant":
        env = item.get("envelope") or {}
        bus = CommandBus(
            queue_dir=str(ROOT / "tasks" / "queue"),
            processed_dir=str(ROOT / "tasks" / "processed"),
        )
        task = bus.envelope_to_task(env)
        q = TaskQueue(queue_dir=str(ROOT / "tasks" / "queue"), processed_dir=str(ROOT / "tasks" / "processed"))
        queued_file = q.add_task(task)
        queued = {
            "status": "queued",
            "task": {"task_id": task.get("task_id"), "intent": task.get("intent"), "goal": task.get("goal")},
            "artifacts": {"queued_task_file": queued_file},
            "policy": {"decision": "CONFIRM", "reason": "approved via callback", "risk": "high"},
            "errors": [],
        }
        item["status"] = "granted"
        item["resolved_at"] = datetime.now().isoformat()
        item["queued_result"] = queued
        pending[request_id] = item
        _save_pending_approvals(pending)
        return {"status": "ok", "callback": cb, "approval_request": {"request_id": request_id, "status": "granted"}, "queued": queued}

    if action in {"approval.deny", "approval.skip"}:
        item["status"] = "denied" if action == "approval.deny" else "skipped"
        item["resolved_at"] = datetime.now().isoformat()
        pending[request_id] = item
        _save_pending_approvals(pending)
        return {"status": "ok", "callback": cb, "approval_request": {"request_id": request_id, "status": item["status"]}}

    return {"status": "error", "errors": ["unsupported_action"], "callback": cb}


def main() -> int:
    ap = argparse.ArgumentParser(description="Graywolf Runtime Kernel")
    ap.add_argument("action", choices=["run-once", "start", "stop", "status", "submit-command", "approval-callback"], help="Runtime action")
    ap.add_argument("--intent", default="")
    ap.add_argument("--payload", default="{}", help="JSON payload for submit-command")
    ap.add_argument("--source", default="cli")
    ap.add_argument("--session-id", default="default", help="Runtime session id")
    ap.add_argument("--callback-data", default="", help="approval callback data, e.g. approval.grant:APR-...")
    ap.add_argument("--actor", default="runtime")
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
    elif args.action == "approval-callback":
        if not args.callback_data:
            out = {"status": "error", "artifacts": {}, "errors": ["callback_data_required"]}
        else:
            out = handle_approval_callback(args.callback_data, actor=args.actor)
    else:
        out = status(args.session_id)

    payload = {"ts": datetime.now().isoformat(), **out}
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if out.get("status") in {"ok", "queued", "confirm_required"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
