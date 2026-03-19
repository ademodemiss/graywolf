"""Assistant UX response explainer (v1.1 wave-1).

Amaç: teknik runtime çıktısını kullanıcı dostu kısa özet cümlelerine çevirmek.
"""
from __future__ import annotations

from typing import Any


FILLER_PHRASES = (
    "harika soru",
    "memnuniyetle",
    "yardımcı olmaktan mutluluk",
    "isterseniz size",
)

ACTION_HINT_WORDS = (
    "çalıştır",
    "kontrol et",
    "incele",
    "deneyebilirsin",
    "kullan",
    "aç",
)


ERROR_REMEDIATION_HINTS: list[tuple[str, str]] = [
    ("invalid_payload_json", "Payload JSON formatını düzeltip komutu tekrar çalıştır."),
    ("confirm_required", "Onay bekleyen isteği `graywolf approvals` ile görüp approve/deny ver."),
    ("permission denied", "Yetki/erişim problemini kontrol et; gerekirse dosya izinlerini doğrula."),
    ("timeout", "Komutu daha dar kapsamla tekrar dene veya loglardan darboğazı kontrol et."),
    ("not found", "Eksik dosya/komut olabilir; yol ve bağımlılıkları kontrol et."),
]


def _remediation_hint(error_text: str) -> str:
    lowered = (error_text or "").lower()
    for needle, hint in ERROR_REMEDIATION_HINTS:
        if needle in lowered:
            return hint
    return "`graywolf logs --target daemon --lines 50` ve `graywolf precheck` ile hızlı teşhis yap."


def score_ux_output(ux: dict[str, str]) -> dict[str, Any]:
    """Hafif UX kalite kontrolü (v1.1).

    Kriterler:
    - summary açık mı?
    - next_step aksiyon içeriyor mu?
    - gereksiz laf var mı?
    """
    summary = (ux or {}).get("summary", "") or ""
    next_step = (ux or {}).get("next_step", "") or ""

    summary_clear = len(summary.strip()) >= 12
    has_action = any(w in next_step.lower() for w in ACTION_HINT_WORDS) or "`" in next_step
    has_filler = any(p in (summary + " " + next_step).lower() for p in FILLER_PHRASES)

    score = int(summary_clear) + int(has_action) + int(not has_filler)
    level = "good" if score == 3 else ("ok" if score == 2 else "weak")

    return {
        "score": score,
        "level": level,
        "checks": {
            "summary_clear": summary_clear,
            "next_step_actionable": has_action,
            "has_filler": has_filler,
        },
    }


def explain_execution(result: dict[str, Any]) -> dict[str, str]:
    status = (result or {}).get("status", "unknown")
    intent = (result or {}).get("intent", "unknown")
    task_id = (result or {}).get("task_id") or ((result or {}).get("task") or {}).get("task_id")
    error_text = (result or {}).get("error") or ""
    if not error_text:
        errs = (result or {}).get("errors")
        if isinstance(errs, list) and errs:
            error_text = " | ".join(str(x) for x in errs)

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
        if error_text:
            summary += f" Hata: {error_text}"
        next_step = _remediation_hint(error_text)
    else:
        summary = f"İş durumu: {status}."
        next_step = "Detay için status/logs komutlarını kullanabilirsin."

    return {"summary": summary, "next_step": next_step}
