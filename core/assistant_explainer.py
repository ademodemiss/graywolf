"""Assistant UX response explainer (v1.1 wave-1).

Amaç: teknik runtime çıktısını kullanıcı dostu kısa özet cümlelerine çevirmek.
"""
from __future__ import annotations

from typing import Any


def explain_execution(result: dict[str, Any]) -> dict[str, str]:
    status = (result or {}).get("status", "unknown")
    intent = (result or {}).get("intent", "unknown")
    task_id = (result or {}).get("task_id") or ((result or {}).get("task") or {}).get("task_id")

    if status == "queued":
        summary = f"İş kuyruğa alındı. Intent: {intent}."
        if task_id:
            summary += f" Task ID: {task_id}."
        next_step = "İstersen `graywolf queue --limit 5` ile takip edebilirsin."
    elif status == "confirm_required":
        summary = f"Bu iş onay bekliyor. Intent: {intent}."
        next_step = "`graywolf approvals` ile bekleyen isteği görüp approve/deny verebilirsin."
    elif status == "denied":
        summary = f"İş policy tarafından reddedildi. Intent: {intent}."
        next_step = "Daha güvenli bir intent veya daha dar kapsamla tekrar deneyebilirsin."
    elif status == "error":
        summary = "İş sırasında hata oluştu."
        next_step = "`graywolf logs --target daemon --lines 50` ve `graywolf precheck` ile hızlı teşhis yap."
    else:
        summary = f"İş durumu: {status}."
        next_step = "Detay için status/logs komutlarını kullanabilirsin."

    return {"summary": summary, "next_step": next_step}
