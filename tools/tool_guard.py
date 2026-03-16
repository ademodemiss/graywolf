from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

from policies.shell_policy import PolicyDecision, ShellPolicy


@dataclass
class ToolMetadata:
    name: str
    module: str
    description: str
    smoke_test: Optional[str] = None
    tags: Sequence[str] = field(default_factory=list)
    requires_env: Sequence[str] = field(default_factory=list)


class ToolRegistry:
    def __init__(self) -> None:
        self._registry: Mapping[str, ToolMetadata] | dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata) -> None:
        if metadata.name in self._registry:
            raise ValueError(f"Tool {metadata.name} already registered")
        self._registry[metadata.name] = metadata

    def get(self, name: str) -> Optional[ToolMetadata]:
        return self._registry.get(name)

    def list(self) -> list[ToolMetadata]:
        return list(self._registry.values())

    def smoke_jobs(self) -> list[ToolMetadata]:
        return [tool for tool in self._registry.values() if tool.smoke_test]


class ToolGuard:
    def __init__(
        self,
        policy: ShellPolicy | None = None,
        log_dir: str = "/home/adem/graywolf/logs",
        registry: ToolRegistry | None = None,
    ) -> None:
        self.policy = policy or ShellPolicy()
        self.log_path = Path(os.path.expanduser(log_dir)) / "tool_guard.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = registry

    def inspect(self, command: str) -> dict:
        entry = self._build_entry(command)
        self._write(entry)
        return entry

    def record_tool_use(
        self,
        tool_name: str,
        command: str,
        result_summary: Mapping[str, object] | None = None,
    ) -> dict:
        metadata = self.registry.get(tool_name) if self.registry else None
        extra_payload = {
            "result_summary": dict(result_summary) if result_summary else {},
        }
        entry = self._build_entry(command, metadata=metadata, extra=extra_payload)
        self._write(entry)
        return entry

    def _build_entry(
        self,
        command: str,
        metadata: ToolMetadata | None = None,
        extra: Mapping[str, object] | None = None,
    ) -> dict:
        decision, reason = self.policy.evaluate(command)
        severity = self._severity(decision, command)
        entry: dict[str, object] = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "command": command,
            "decision": decision.value,
            "reason": reason,
            "severity": severity,
        }
        if metadata:
            entry.update(
                {
                    "tool_name": metadata.name,
                    "tool_module": metadata.module,
                    "tool_description": metadata.description,
                    "tool_tags": list(metadata.tags),
                }
            )
        if extra:
            entry.update(extra)
        return entry

    def _severity(self, decision: PolicyDecision, command: str) -> str:
        normalized = command.lower()
        if decision == PolicyDecision.DENY or "rm -rf" in normalized:
            return "critical"
        if decision == PolicyDecision.CONFIRM or any(token in normalized for token in ["&&", "||", ";"]):
            return "warning"
        if any(flag in normalized for flag in [">", "<", "curl", "wget"]):
            return "medium"
        return "low"

    def _write(self, entry: dict) -> None:
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def summarize(self, limit: int = 5) -> list[dict]:
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()[-limit:]
        return [json.loads(line) for line in lines]

    def registry_summary(self) -> list[dict]:
        if not self.registry:
            return []
        return [
            {
                "tool": tool.name,
                "module": tool.module,
                "description": tool.description,
                "smoke_test": tool.smoke_test,
            }
            for tool in self.registry.list()
        ]


def run_test() -> dict:
    guard = ToolGuard()
    sample = "ls -l"
    info = guard.inspect(sample)
    return {"status": "ok", "guard": "active", "last": info}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GrayWolf tool guard")
    parser.add_argument("--test", action="store_true", help="Run a self-test")
    parser.add_argument("--command", help="Inspect a command")
    args = parser.parse_args()

    guard = ToolGuard()
    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    elif args.command:
        print(json.dumps(guard.inspect(args.command), ensure_ascii=False))
    else:
        print(json.dumps({"status": "idle"}))
