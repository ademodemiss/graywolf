import datetime
import json
from pathlib import Path
from typing import Mapping

from core.event_bus import BUS
from core.event_types import EventTypes
from monitor.telegram_alert import send_telegram_message


class ReplanNotifier:
    def __init__(self, bus=None, log_dir: str = "/home/adem/graywolf/logs"):
        self.bus = bus or BUS
        self.log_path = Path(log_dir) / "replan_notifier.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.bus.subscribe(EventTypes.REPLAN_READY, self._on_ready)
        self.bus.subscribe(EventTypes.REPLAN_EXECUTED, self._on_executed)

    def _on_ready(self, event: Mapping[str, object]):
        payload = event.get("payload") or {}
        self._log("ready", payload)
        message = self._format_ready(payload)
        send_telegram_message(message)

    def _on_executed(self, event: Mapping[str, object]):
        payload = event.get("payload") or {}
        self._log("executed", payload)
        message = self._format_executed(payload)
        send_telegram_message(message)

    def _format_ready(self, payload: Mapping[str, object]) -> str:
        original_error = payload.get("original_error") or {}
        new_plan = payload.get("new_plan") or []
        lines = [
            f"[Replan hazır] workflow={payload.get('workflow_name')}",
            f"Hint: {payload.get('hint')}",
            f"Hata: {original_error.get('stderr_snippet') or original_error.get('stderr') or 'bilinmiyor'}",
            f"Yeni plan uzunluğu: {len(new_plan)} adım",
        ]
        return "\n".join(lines)

    def _format_executed(self, payload: Mapping[str, object]) -> str:
        replan_result = payload.get("replan_result") or {}
        statuses = []
        for step in replan_result.get("results", []):
            statuses.append(f"{step.get('name')}:{step.get('status')}")
        status_line = " | ".join(statuses) if statuses else "(sonuç yok)"
        lines = [
            f"[Replan tamamlandı] workflow={payload.get('workflow_name')}",
            f"Görev durumu: {replan_result.get('status')}",
            f"Adım sonuçları: {status_line}",
        ]
        if payload.get("replan_info"):
            lines.append(f"Hint: {payload['replan_info'].get('hint')}")
        return "\n".join(lines)

    def _log(self, stage: str, payload: Mapping[str, object]):
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "stage": stage,
            "payload": payload,
        }
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
