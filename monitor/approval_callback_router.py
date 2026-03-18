"""Telegram callbacklarını EventBus üzerinde APP* olaylarına çeviren yönlendirici."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping

from core.approval import ApprovalState
from core.event_bus import BUS
from core.event_types import EventTypes


class ApprovalCallbackRouter:
    _ACTION_MAP = {
        "approval.grant": (EventTypes.APPROVAL_GRANTED, ApprovalState.GRANTED),
        "approval.deny": (EventTypes.APPROVAL_DENIED, ApprovalState.DENIED),
        "approval.skip": (EventTypes.APPROVAL_SKIPPED, ApprovalState.SKIPPED),
    }

    def __init__(self, bus=None, log_dir: str | None = None) -> None:
        self.bus = bus or BUS
        root = Path(__file__).resolve().parents[1]
        resolved_log_dir = Path(log_dir) if log_dir else (root / "logs")
        self.log_path = resolved_log_dir / "approval_callbacks.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def handle_callback(self, callback_data: str, actor: str | None = None, metadata: Mapping[str, object] | None = None) -> dict:
        metadata = metadata or {}
        parts = callback_data.split(":", 1)
        action = parts[0]
        request_id = parts[1] if len(parts) == 2 else None

        if not action or not request_id:
            raise ValueError(f"Invalid callback_data '{callback_data}'")

        mapping = self._ACTION_MAP.get(action)
        if not mapping:
            raise ValueError(f"Unrecognized approval callback action '{action}'")

        event_type, state = mapping
        payload = {
            "request_id": request_id,
            "status": state.value,
            "actor": actor,
            "metadata": metadata,
        }
        self._log(action, payload)
        self.bus.publish(event_type, payload)
        return {"event": event_type, "status": state.value}

    def _log(self, action: str, payload: Mapping[str, object]) -> None:
        entry = {"action": action, "payload": payload}
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(str(entry) + "\n")
