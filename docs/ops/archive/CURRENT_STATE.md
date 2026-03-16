# GrayWolf Current Project State

## Overview
GrayWolf v1.2.0 (Hardened Autonomy) şu anda Phase 263 replan hattının canlıya alınmasıyla birlikte Phase 264’ün izleme ve operasyona destek katmanlarını inşa etmeye odaklanıyor. Replan → self-improve → Telegram → ApprovalManager köprüsü çalışır durumda; Phase 264’te bu hattın sağlığını ölçen dashboard/doküman ve script katmanları geliştiriliyor.

## Phase Status Summary
*   **✅ Verified (v1.1.0):** Faz 1-5 Analizi ve Temel Kurulumlar tamamlandı; Phase 261/262 replan/self-improve altyapıları doğrulandı; Phase 263 replan bildirim hattı EventBus + Telegram + ApprovalManager entegrasyonu ile tamamlandı.
*   **🟡 In Progress (v1.2.0):** Phase 264 – Replan geri bildirimlerinin izlenebilirliğini artıracak monitoring dokümantasyonu, dashboard kartları ve `monitor/approval_health.py` gibi sağlık raporu araçları geliştiriliyor.
*   **⚪ Planned:** Phase 265 – Approval status == GRANTED olan self-improve analizlerini otomatik görev önerilerine dönüştürme ve replan geri bildirimi üzerine learning döngüsünü genişletme.

## Next Planned Action
1. `monitor/approval_health.py` çıktısını (log özetlerini) deploy/ops kanallarında paylaşarak canlıya alma öncesi `replan_bridge` sağlık durumunu doğrula.
2. `docs/phase264_monitoring.md` ve `NEXT_ACTION.md` üzerinden operasyonel kontrol listesini güncel tut, gerektiğinde Slack/Telegram raporları üret.
3. `planning/phase265_plan.md` dosyasında Phase 264 çıktıları üzerine `self_improve_replan` hakemliklerine dayanan otomatik öneri/adaptasyon adımlarını taslaklaştır.

## Key Directives (from SOUL.md - for quick reference)
*   Max context: 200k tokens per request.
*   Logs: Summary (max 20-40 lines).
*   Evidence: Read only specific files, not whole directories.
*   Roadmap: Use CURRENT_STATE.md for overview, full roadmap only if needed.
*   Memory: File-based (LLM memory ❌, File memory ✅).
*   Rate Limit: No retry spam, `blocked_rate_limit` state on limit hit.
*   Phase Progression: Proceed in roadmap order. Do not regress to earlier phases if VERIFIED.
