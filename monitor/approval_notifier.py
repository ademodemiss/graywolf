import datetime
import json
from pathlib import Path
from typing import Mapping

from core.event_bus import BUS
from core.event_types import EventTypes
from monitor.telegram_alert import send_telegram_message


class ApprovalNotifier:
    def __init__(self, bus=None, log_dir: str = "/home/adem/graywolf/logs"):
        self.bus = bus or BUS
        self.log_path = Path(log_dir) / "approval_notifier.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.bus.subscribe(EventTypes.APPROVAL_REQUESTED, self._on_request)
        self.bus.subscribe(EventTypes.APPROVAL_GRANTED, self._on_update)
        self.bus.subscribe(EventTypes.APPROVAL_DENIED, self._on_update)
        self.bus.subscribe(EventTypes.APPROVAL_SKIPPED, self._on_update)

    def _on_request(self, event: Mapping[str, object]):
        payload = event.get("payload") or {}
        self._log("requested", payload)
        text, reply_markup = self._format_message(payload, status="pending")
        send_telegram_message(text, reply_markup=reply_markup)

    def _on_update(self, event: Mapping[str, object]):
        payload = event.get("payload") or {}
        status = payload.get("status") or "updated"
        self._log(status, payload)
        text, reply_markup = self._format_message(payload, status=status)
        send_telegram_message(text, reply_markup=reply_markup)

    def _format_message(self, payload: Mapping[str, object], status: str) -> tuple[str, dict | None]:
        base = (
            f"[Approval {status}] Request {payload.get('request_id')}\n"
            f"Command: {payload.get('command')}\n"
            f"Category: {payload.get('category')}\n"
        )
        if status == "pending":
            base += "Butonlara tıklayarak Onayla ✅ / Reddet ❌ şeklinde yanıt verebilirsiniz."
            reply_markup = {
                "inline_keyboard": [
                    [
                        {"text": "Onayla ✅", "callback_data": f"approval.grant:{payload.get('request_id')}"},
                        {"text": "Reddet ❌", "callback_data": f"approval.deny:{payload.get('request_id')}"},
                    ]
                ]
            }
            return base, reply_markup
        return base + "Durum: " + status, None

    def _log(self, stage: str, payload: Mapping[str, object]):
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "stage": stage,
            "payload": payload,
        }
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
