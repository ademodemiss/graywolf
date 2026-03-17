"""Simulation script: workflow with risky command triggers approval notifier/router."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from time import sleep

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from core.event_bus import BUS
from core.event_types import EventTypes
from monitor.approval_callback_router import ApprovalCallbackRouter
from workflows.runner import run_workflow


router = ApprovalCallbackRouter()
auto_granted: list[str] = []


def auto_grant(event: dict) -> None:
    payload = event.get("payload") or {}
    request_id = payload.get("request_id")
    if not request_id:
        return
    router.handle_callback(f"approval.grant:{request_id}", actor="simulator")
    auto_granted.append(request_id)


BUS.subscribe(EventTypes.APPROVAL_REQUESTED, auto_grant)

workflow = {
    "steps": [
        {"name": "risky-move", "cmd": "mv /tmp/graywolf_dummy_source /tmp/graywolf_dummy_dest"}
    ]
}

print("Starting workflow with human gate...")
result = run_workflow(workflow)
print(json.dumps(result, ensure_ascii=False, indent=2))
print("Auto granted requests:", auto_granted)
