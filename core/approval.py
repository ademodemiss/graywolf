from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

import time

from core.event_bus import EventBus, BUS as GLOBAL_BUS
from core.event_types import EventTypes
from policies.shell_policy import PolicyDecision, ShellPolicy


class ApprovalState(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    SKIPPED = "skipped"


@dataclass
class ApprovalRequest:
    request_id: str
    command: str
    category: str
    requested_by: str | None = None
    status: ApprovalState = ApprovalState.PENDING
    reason: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "command": self.command,
            "category": self.category,
            "requested_by": self.requested_by,
            "status": self.status.value,
            "reason": self.reason,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


class ApprovalManager:
    def __init__(self, bus: EventBus | None = None, policy: ShellPolicy | None = None, auto_grant_allow: bool = False):
        self.bus = bus or GLOBAL_BUS
        self.policy = policy or ShellPolicy()
        self.auto_grant_allow = auto_grant_allow
        self._requests: dict[str, ApprovalRequest] = {}
        self._listeners: dict[str, list[Callable[[ApprovalRequest], None]]] = {}

        self.bus.subscribe(EventTypes.APPROVAL_GRANTED, self._on_granted)
        self.bus.subscribe(EventTypes.APPROVAL_DENIED, self._on_denied)
        self.bus.subscribe(EventTypes.APPROVAL_SKIPPED, self._on_skipped)

    def evaluate_command(self, command: str, requested_by: str | None = None, category_hint: str | None = None) -> tuple[ApprovalRequest | None, str]:
        decision, message = self.policy.evaluate(command)

        if decision == PolicyDecision.ALLOW and self.auto_grant_allow:
            request = self._build_request(command, category_hint or "allowed", requested_by, message)
            request.status = ApprovalState.GRANTED
            self._record(request)
            self._publish(EventTypes.APPROVAL_GRANTED, request)
            return request, message

        if decision == PolicyDecision.ALLOW:
            return None, message

        if decision == PolicyDecision.DENY:
            request = self._build_request(command, category_hint or "denied", requested_by, message)
            request.status = ApprovalState.DENIED
            self._record(request)
            self._publish(EventTypes.APPROVAL_DENIED, request)
            return request, message

        request = self._build_request(command, category_hint or "confirm", requested_by, message)
        self._record(request)
        self._publish(EventTypes.APPROVAL_REQUESTED, request)
        return request, message

    def _build_request(self, command: str, category: str, requested_by: str | None, reason: str | None) -> ApprovalRequest:
        request_id = str(uuid4())
        return ApprovalRequest(
            request_id=request_id,
            command=command,
            category=category,
            requested_by=requested_by,
            reason=reason,
        )

    def _record(self, request: ApprovalRequest):
        self._requests[request.request_id] = request

    def _publish(self, event_type: str, request: ApprovalRequest):
        try:
            self.bus.publish(event_type, request.to_payload())
        except Exception:
            pass

    def _on_granted(self, event: dict):
        self._update_status(event, ApprovalState.GRANTED)

    def _on_denied(self, event: dict):
        self._update_status(event, ApprovalState.DENIED)

    def _on_skipped(self, event: dict):
        self._update_status(event, ApprovalState.SKIPPED)

    def _update_status(self, event: dict, status: ApprovalState):
        payload = event.get("payload", {})
        request_id = payload.get("request_id")
        request = self._requests.get(request_id)
        if not request:
            return
        request.status = status
        request.reason = payload.get("reason", request.reason)
        self._notify_listeners(request)

    def add_listener(self, event_name: str, listener: Callable[[ApprovalRequest], None]):
        self._listeners.setdefault(event_name, []).append(listener)

    def _notify_listeners(self, request: ApprovalRequest):
        listeners = self._listeners.get(request.status.value, [])
        for listener in listeners:
            listener(request)

    def wait_for_status(self, request_id: str, target: set[ApprovalState], timeout_seconds: int = 120) -> ApprovalRequest | None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            request = self._requests.get(request_id)
            if request and request.status in target:
                return request
            time.sleep(0.4)
        return self._requests.get(request_id)

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        return self._requests.get(request_id)

    def pending_requests(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == ApprovalState.PENDING]


if __name__ == "__main__":
    manager = ApprovalManager()
    req, _ = manager.evaluate_command("rm -rf /tmp/important", requested_by="agent")
    if req:
        print(json.dumps(req.to_payload(), ensure_ascii=False, indent=2))
