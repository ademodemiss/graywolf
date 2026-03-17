#!/usr/bin/env python3
"""Session state store for Graywolf runtime (v2 Job 3)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class SessionStateStore:
    def __init__(self, root: str = "/home/adem/graywolf/sessions"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def load(self, session_id: str) -> dict:
        p = self._path(session_id)
        if not p.exists():
            return {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": None,
                "last_command": None,
                "last_result": None,
                "last_error": None,
                "active_task": None,
                "history_count": 0,
            }
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("session_id", session_id)
        data.setdefault("history_count", 0)
        return data

    def save(self, session_id: str, state: dict) -> str:
        state["updated_at"] = datetime.now().isoformat()
        p = self._path(session_id)
        p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return str(p)

    def record(self, session_id: str, *, command: dict | None = None, result: Any = None, error: str | None = None, active_task: str | None = None) -> dict:
        state = self.load(session_id)
        if command is not None:
            state["last_command"] = command
        if result is not None:
            state["last_result"] = result
        if error is not None:
            state["last_error"] = error
        if active_task is not None:
            state["active_task"] = active_task
        state["history_count"] = int(state.get("history_count", 0)) + 1
        state_path = self.save(session_id, state)
        state["state_file"] = state_path
        return state
