import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from core.llm_router import LLMRouter


class SelfImproveTool:
    SUCCESS_KEYWORDS = {"success", "completed", "ok", "done"}
    WARNING_KEYWORDS = {"warn", "warning", "partial", "soft", "alert"}
    FAILURE_KEYWORDS = {"fail", "failed", "error", "denied", "reject", "timeout"}
    CATEGORY_SCORES = {"success": 95, "warning": 65, "failure": 20, "unknown": 50}

    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.llm = self.llm_router.get()

    def analyze_logs_for_improvements(
        self,
        log_content: str,
        context: str = "",
        replan_summary: str | None = None,
    ) -> dict:
        """Verilen log içeriğini ve isteğe bağlı replan özetini analiz edip öneriler döner."""
        context_lines = [line for line in (context or "").splitlines() if line.strip()]
        if replan_summary:
            context_lines.extend(["Replan özeti:", replan_summary])
        combined_context = "\n".join(context_lines)

        prompt = (
            "Aşağıdaki log içeriğini incele ve GrayWolf ajanının performansını artırmak, "
            "hataları azaltmak ya da daha verimli çalışması için öneriler üret. "
            "Yanıtını 200 kelimeyi geçmeyecek şekilde sadece Türkçe olarak ver."
            f"\n\nBağlam:\n{combined_context}\n\nLog İçeriği:\n```\n{log_content}\n```"
        )

        try:
            raw_response = self.llm.generate_response(prompt)
            analysis_text = raw_response[0] if isinstance(raw_response, (tuple, list)) else raw_response
            analysis_text = analysis_text or ""
            return {"status": "ok", "analysis": analysis_text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_past_errors_summary(self, error_logs_path: str = "/home/adem/graywolf/logs/terminal.log", num_errors: int = 5) -> dict:
        errors = []
        if not os.path.exists(error_logs_path):
            return {"status": "warning", "message": "Log dosyası bulunamadı.", "errors": []}

        try:
            with open(error_logs_path, "r", encoding="utf-8") as f:
                for line in reversed(f.readlines()):
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get("status") == "error" or log_entry.get("decision") in {"deny", "needs_confirmation"}:
                            errors.append(log_entry)
                            if len(errors) >= num_errors:
                                break
                    except json.JSONDecodeError:
                        continue
            return {"status": "ok", "errors": errors}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def summarize_replan_events(self, log_path: str, limit: int = 5) -> str:
        if not log_path:
            return ""
        path_obj = Path(log_path)
        if not path_obj.exists():
            return ""

        summary_lines: list[str] = []
        try:
            with path_obj.open("r", encoding="utf-8") as fh:
                for line in reversed(fh.readlines()):
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    stage = entry.get("stage", "unknown")
                    payload = entry.get("payload", {}) or {}
                    workflow = payload.get("workflow_name") or payload.get("workflow") or "bilinmeyen"
                    hint = payload.get("hint") or "yok"

                    if stage == "ready":
                        original_error = payload.get("original_error", {})
                        error_desc = (
                            original_error.get("stderr_snippet")
                            or original_error.get("stderr")
                            or original_error.get("message")
                            or "bilinmiyor"
                        )
                        summary = f"[Hazır] workflow={workflow} hint={hint} error={error_desc}"
                    else:
                        replan_result = payload.get("replan_result", {})
                        status = replan_result.get("status") or payload.get("info", {}).get("status") or "bilinmiyor"
                        step_statuses = " | ".join(
                            f"{step.get('name')}:{step.get('status')}" for step in replan_result.get("results", [])
                        )
                        summary = f"[Tamamlandı] workflow={workflow} status={status}"
                        if step_statuses:
                            summary += f" adımlar={step_statuses}"

                    summary_lines.append(summary)
                    if len(summary_lines) >= limit:
                        break
        except Exception:
            return ""

        return "\n".join(reversed(summary_lines)) if summary_lines else ""

    @staticmethod
    def improve_from_replan_entries(
        entries: list[dict],
        limit: int = 5,
    ) -> list[dict]:
        jobs: list[dict] = []
        if not entries:
            return jobs

        for entry in entries:
            if len(jobs) >= limit:
                break

            approval_request = (entry.get("approval_request") or {})
            if approval_request.get("status") != "GRANTED":
                continue

            payload = (entry.get("payload") or {})
            analysis = (entry.get("analysis") or {})
            workflow = payload.get("workflow_name") or payload.get("workflow") or "bilinmeyen"
            replan_reason = payload.get("hint") or payload.get("reason") or payload.get("workflow_reason") or "bilinmiyor"

            analysis_summary = analysis.get("summary") or analysis.get("details") or ""
            start_source = (
                payload.get("workflow_source")
                or payload.get("workflow_name")
                or payload.get("workflow")
                or payload.get("workflow_input")
                or entry.get("stage")
                or "bilinmeyen"
            )
            job = {
                "request_id": approval_request.get("request_id"),
                "event": entry.get("event"),
                "workflow": workflow,
                "analysis_status": analysis.get("status"),
                "analysis_summary": analysis_summary,
                "replan_reason": replan_reason,
                "approved_at": approval_request.get("granted_at") or approval_request.get("created_at"),
                "timestamp": entry.get("ts"),
                "payload": payload,
                "approval": approval_request,
                "start_source": start_source,
                "learning_feedback": analysis_summary,
                "learning_status": "scheduled",
            }
            jobs.append(job)

        return jobs

    @staticmethod
    def _determine_category(summary: str, status: str) -> str:
        combined = f"{(summary or "").lower()} {(status or "").lower()}"
        for keyword in SelfImproveTool.FAILURE_KEYWORDS:
            if keyword in combined:
                return "failure"
        for keyword in SelfImproveTool.WARNING_KEYWORDS:
            if keyword in combined:
                return "warning"
        for keyword in SelfImproveTool.SUCCESS_KEYWORDS:
            if keyword in combined:
                return "success"
        return "unknown"

    @staticmethod
    def _score_for_category(category: str) -> int:
        return SelfImproveTool.CATEGORY_SCORES.get(
            category,
            SelfImproveTool.CATEGORY_SCORES.get("unknown", 50),
        )

    @staticmethod
    def execute_pending_job(job: dict) -> dict:
        summary = (job.get("analysis_summary") or job.get("learning_feedback") or "").strip()
        if not summary:
            analysis = (job.get("analysis") or {})
            summary = (analysis.get("summary") or analysis.get("details") or "").strip()
        status = (job.get("analysis_status") or job.get("learning_status") or "scheduled").lower()
        category = SelfImproveTool._determine_category(summary, status)
        reliability = SelfImproveTool._score_for_category(category)
        if category == "unknown":
            category = "success"
            final_status = "completed"
            reliability = SelfImproveTool.CATEGORY_SCORES.get("success", reliability)
        else:
            final_status = (
                "completed" if category == "success" else
                "warning" if category == "warning" else
                "failed"
            )
        baseline_follow_up = job.get("learning_follow_up_notes") or summary or job.get("analysis_status") or final_status
        follow_up = baseline_follow_up.strip()
        if not follow_up:
            follow_up = final_status
        note_suffix = " (scheduler executed job)"
        if note_suffix not in follow_up:
            follow_up = f"{follow_up}{note_suffix}"
        learning_feedback = job.get("learning_feedback") or summary or f"workflow {job.get('workflow')} {final_status}"
        analysis_summary = summary or job.get("analysis_summary") or follow_up
        return {
            "analysis_status": final_status,
            "analysis_summary": analysis_summary,
            "learning_status": final_status,
            "learning_feedback": learning_feedback,
            "learning_feedback_category": category,
            "learning_reliability_score": reliability,
            "learning_follow_up_notes": follow_up,
        }

    def _read_file_content(self, path: str) -> str:
        if not path:
            return ""
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception:
            return ""

    def append_report(self, report_path: str, content: str) -> dict:
        if not report_path:
            return {"status": "error", "message": "report_path belirtilmedi."}

        try:
            directory = os.path.dirname(report_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            timestamp = datetime.now(timezone.utc).isoformat()
            with open(report_path, "a", encoding="utf-8") as fh:
                fh.write(f"{timestamp} - {content}\n")
            return {"status": "success", "path": report_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Kendi Kendini İyileştirme Aracı")
    parser.add_argument("--action", required=True, choices=["analyze_logs", "get_errors_summary"], help="Yapılacak eylem")
    parser.add_argument("--log_content", help="Analiz edilecek log içeriği (analyze_logs için)")
    parser.add_argument("--log_path", help="Analiz edilecek log dosyası yolu (analyze_logs için)")
    parser.add_argument("--context", default="", help="Analiz için ek bağlam (analyze_logs için)")
    parser.add_argument("--include_replan", action="store_true", help="Replan olaylarını bağlam içinde dahil et")
    parser.add_argument("--replan_log_path", default="/home/adem/graywolf/logs/replan_notifier.log", help="Replan log dosyası (include_replan ile)")
    parser.add_argument("--report_path", default="", help="Analiz sonucunun yazılacağı dosya (opcional)")
    parser.add_argument("--error_logs_path", default="/home/adem/graywolf/logs/terminal.log", help="Hata loglarının yolu (get_errors_summary için)")
    parser.add_argument("--num_errors", type=int, default=5, help="Çekilecek hata sayısı (get_errors_summary için)")

    args = parser.parse_args()

    llm_router = LLMRouter()
    tool = SelfImproveTool(llm_router)

    if args.action == "analyze_logs":
        log_content = args.log_content or ""
        if args.log_path:
            log_content = tool._read_file_content(args.log_path)

        replan_summary = ""
        if args.include_replan:
            replan_summary = tool.summarize_replan_events(args.replan_log_path)

        result = tool.analyze_logs_for_improvements(log_content, args.context, replan_summary)

        if result.get("status") == "ok" and args.report_path:
            append_result = tool.append_report(args.report_path, result.get("analysis", ""))
            if append_result.get("status") != "success":
                result = {"status": "error", "error": append_result.get("message")}

        print(json.dumps(result, ensure_ascii=False))
    elif args.action == "get_errors_summary":
        result = tool.get_past_errors_summary(args.error_logs_path, args.num_errors)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
