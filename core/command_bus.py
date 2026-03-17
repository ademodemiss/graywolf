#!/usr/bin/env python3
"""Graywolf Unified Command Bus (CLI-first, v2 Job 2)."""

from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from core.task_queue import TaskQueue


class CommandBus:
    def __init__(self, queue_dir: str, processed_dir: str):
        self.queue = TaskQueue(queue_dir=queue_dir, processed_dir=processed_dir)

    @staticmethod
    def build_envelope(intent: str, payload: dict, source: str = "cli", command_id: str | None = None) -> dict:
        cid = command_id or f"CMD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        return {
            "command_id": cid,
            "intent": intent,
            "payload": payload or {},
            "source": source,
            "created_at": datetime.now().isoformat(),
        }

    @staticmethod
    def envelope_to_task(envelope: dict) -> dict:
        payload = envelope.get("payload") or {}
        goal = payload.get("goal") or payload.get("text") or envelope.get("intent")
        task_id = f"TASK-{envelope['command_id']}"
        return {
            "task_id": task_id,
            "command_id": envelope.get("command_id"),
            "source": envelope.get("source"),
            "intent": envelope.get("intent"),
            "goal": goal,
            "payload": payload,
        }

    def submit(self, envelope: dict) -> dict:
        task = self.envelope_to_task(envelope)
        artifact = self.queue.add_task(task)
        return {
            "status": "queued",
            "command": envelope,
            "task": {
                "task_id": task.get("task_id"),
                "goal": task.get("goal"),
                "intent": task.get("intent"),
            },
            "artifacts": {
                "queued_task_file": artifact,
            },
            "errors": [],
        }


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Graywolf Command Bus")
    p.add_argument("--intent", required=True)
    p.add_argument("--payload", default="{}", help="JSON payload")
    p.add_argument("--source", default="cli")
    p.add_argument("--queue-dir", default="/home/adem/graywolf/tasks/queue")
    p.add_argument("--processed-dir", default="/home/adem/graywolf/tasks/processed")
    args = p.parse_args()

    payload = json.loads(args.payload)
    bus = CommandBus(queue_dir=args.queue_dir, processed_dir=args.processed_dir)
    env = bus.build_envelope(intent=args.intent, payload=payload, source=args.source)
    out = bus.submit(env)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
