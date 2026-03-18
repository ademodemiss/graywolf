"""Agent dispatcher (aktif, minimal/no-break).

Decomposer adımlarını CommandBus üzerinden queue'ya yollar.
"""
from __future__ import annotations

from typing import Any

from agent.task_decomposer import plan_summary_from_command
from core.command_bus import CommandBus


class Dispatcher:
    def __init__(self, queue_dir: str, processed_dir: str):
        self.bus = CommandBus(queue_dir=queue_dir, processed_dir=processed_dir)

    def dispatch(self, command: str) -> dict[str, Any]:
        bundle = plan_summary_from_command(command)
        results: list[dict[str, Any]] = []

        for step in bundle["decomposed_steps"]:
            envelope = self.bus.build_envelope(
                intent=step["intent"],
                payload=step["payload"],
                source=step.get("source", "agent-dispatcher"),
            )
            out = self.bus.submit(envelope)
            results.append(
                {
                    "step_id": step["id"],
                    "intent": step["intent"],
                    "status": out.get("status"),
                    "task_id": (out.get("task") or {}).get("task_id"),
                    "policy": out.get("policy"),
                }
            )

        return {
            "objective": bundle["plan"]["objective"],
            "plan": bundle["plan"],
            "steps_executed": results,
        }
