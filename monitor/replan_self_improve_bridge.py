import datetime
import json
from pathlib import Path
from typing import Mapping

from core.approval import ApprovalManager, ApprovalRequest
from core.event_bus import BUS
from core.event_types import EventTypes
from core.llm_router import LLMRouter
from monitor.telegram_alert import send_telegram_message
from tools.self_improve_tool import SelfImproveTool


class ReplanSelfImproveBridge:
    def __init__(
        self,
        bus=None,
        log_dir: str = "/home/adem/graywolf/logs",
        replan_log_path: str = "/home/adem/graywolf/logs/replan_notifier.log",
        tool: SelfImproveTool | None = None,
        approval_manager: ApprovalManager | None = None,
    ):
        self.bus = bus or BUS
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.replan_log_path = Path(replan_log_path)
        self.report_path = self.log_dir / "self_improve_replan.log"
        self.tool = tool or SelfImproveTool(LLMRouter())
        self.approval_manager = approval_manager or ApprovalManager()

        self.bus.subscribe(EventTypes.REPLAN_READY, self._handle_event)
        self.bus.subscribe(EventTypes.REPLAN_EXECUTED, self._handle_event)

    def _handle_event(self, event: Mapping[str, object]):
        payload = event.get("payload") or {}
        summary = self.tool.summarize_replan_events(str(self.replan_log_path))
        context = self._build_context(event["type"], payload, summary)
        analysis = self.tool.analyze_logs_for_improvements("", context, summary or None)
        approval_request = self._maybe_request_approval(event["type"], payload, summary)
        message = self._format_message(event["type"], payload, summary, analysis, approval_request)
        send_telegram_message(message)
        self._log(event["type"], payload, summary, analysis, approval_request)

    def _build_context(self, event_type: str, payload: Mapping[str, object], summary: str | None) -> str:
        parts = [f"Olay: {event_type}", f"Workflow: {payload.get('workflow_name', 'bilinmiyor')}" ]
        if payload.get("hint"):
            parts.append(f"Hint: {payload['hint']}")
        if summary:
            parts.append(f"Replan özeti: {summary}")
        return "\n".join(parts)

    def _maybe_request_approval(
        self,
        event_type: str,
        payload: Mapping[str, object],
        summary: str | None,
    ) -> ApprovalRequest | None:
        if event_type != EventTypes.REPLAN_READY:
            return None

        workflow_name = payload.get("workflow_name", "bilinmeyen")
        hint = payload.get("hint")
        summary_text = summary or hint or "Yeni replan önerisi"
        command = f"replan {workflow_name} : {summary_text[:200]}"
        request, _ = self.approval_manager.evaluate_command(
            command,
            requested_by="replan_bridge",
            category_hint="replan",
        )
        if request:
            request.metadata.setdefault("replan", {}).update(
                {
                    "summary": summary_text,
                    "event": event_type,
                    "hint": hint,
                }
            )
        return request

    def _format_message(
        self,
        event_type: str,
        payload: Mapping[str, object],
        summary: str | None,
        analysis: dict,
        approval_request: ApprovalRequest | None,
    ) -> str:
        lines = [f"[Replan {event_type}] workflow={payload.get('workflow_name', 'bilinmeyen')} "]
        if summary:
            lines.append(f"Replan özeti:\n{summary}")
        analysis_text = analysis.get("analysis")
        if analysis_text:
            lines.append(f"SelfImprove önerisi:\n{analysis_text}")
        status = analysis.get("status") or "bilinmiyor"
        lines.append(f"Analiz durumu: {status}")
        if approval_request:
            lines.append(f"Approval talebi: {approval_request.request_id} (durum: {approval_request.status.value})")
        if status != "ok":
            lines.append(f"Hata: {analysis.get('error', 'bilinmiyor')}")
        return "\n".join(lines)

    def _log(
        self,
        event_type: str,
        payload: Mapping[str, object],
        summary: str | None,
        analysis: dict,
        approval_request: ApprovalRequest | None,
    ):
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event": event_type,
            "payload": payload,
            "summary": summary,
            "analysis": analysis,
            "approval_request": approval_request.to_payload() if approval_request else None,
        }
        with open(self.report_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
