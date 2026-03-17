# Graywolf Canonical Project State

_Last updated: 2026-03-17_

Bu dosya projedeki **tek gerçek durum özeti**dir. Yeni gelen biri önce bunu okumalı.

---

## 1) Projenin net amacı
**Graywolf = kendi runtime’ı olan otonom operasyon motoru**

Hedef ürün davranışı:
1. Komut/hedef alır
2. Planlar ve göreve çevirir
3. Güvenlik/onay kurallarını uygular
4. Çalıştırır
5. Kanıt/rapor/log üretir
6. Hata olursa replan/recovery yapar

---

## 2) Şu an çalışan çekirdek (gerçek durum)
- Autonomy worker/daemon: `scripts/autonomy_daemon.sh`, `scripts/run_autonomy_worker.py`
- Queue + loop: `core/task_queue.py`, `core/autonomous_loop.py`
- Orchestrator + LLM fallback: `core/orchestrator.py`, `core/llm_router.py`
- Approval + event bus: `core/approval.py`, `core/event_bus.py`, `monitor/approval_callback_router.py`
- Replan/self-improve zinciri: `monitor/replan_self_improve_bridge.py`, `monitor/replan_self_improve_scheduler.py`
- Ops komutları: `scripts/daily_healthcheck.sh`, `scripts/operator_tasks.sh`, `scripts/run_three_real_tasks.sh`
- Risk özeti: `scripts/risk_summary_from_terminal.sh`
- Dashboard: `dashboard/server.py`

Durum seviyesi: **v2 Foundation Freeze / stabil çalışır**

---

## 3) Bugüne kadar yapılan kritik ilerlemeler
- LLM router fallback uyumsuzluğu giderildi (string/tuple normalize).
- Orchestrator’a kalite filtresi ve unknown-tool fallback eklendi.
- 3 gerçek görev akışı (repo/health/risk) çalışır doğrulandı.
- Görev kalite skoru (quality_score + average_quality_score) eklendi.
- Financial data tarafında doğrulama + kalite meta katmanı eklendi.
- Extended self-improve regression suite eklendi: `scripts/self_improve_regression.sh`.
- RC handoff ve 24 saat monitoring planı çıkarıldı.

Referans raporlar:
- `reports/release_candidate_handoff_2026-03-17.md`
- `reports/final_phase_report.md`
- `docs/ops/POST_RELEASE_24H_MONITORING_PLAN.md`

---

## 4) Neden karıştı? (teknik kök neden)
- Farklı ajanlarla paralel geliştirme
- Session reset/silme sonrası bağlam kaybı
- Aynı işleve giden birden fazla dosya/akış (duplicate runtime yolları)
- Plan/durum dokümanlarının dağınık olması

---

## 5) Çakışan alanlar (temizlenecek)
1. Çoklu runtime/loop kontrol dosyaları
   - `core/full_autonomy.py`
   - `core/full_autonomy_controller.py`
   - `core/agent_loop.py`
   - `core/service_runner.py`
2. Çift workflow execution hattı
   - `workflows/runner.py`
   - `workflow_engine/workflow_executor.py`
3. Komut intake prototipleri runtime’a tam bağlı değil
   - `agent/command_parser.py`
   - `agent/task_decomposer.py`
   - `agent/dispatcher.py`

---

## 6) Eksik parçalar (v2 için gerçek boşluk)
- Tekil runtime kernel (single entrypoint + lifecycle)
- Session yönetimi (stateful runtime içi oturum katmanı)
- Unified interface layer (CLI/Telegram/API → tek command bus)
- Tek ve zorunlu command->task->response sözleşmesi

Not (2026-03-17 karar): `agent/*` intake prototipleri canonical runtime hattına bağlanmayacak; freeze/deprecate edilip cleanup turunda `archive/` altına taşınacak.

---

## 7) Graywolf v2 birleşim planı (yeniden yazmadan)
### Aşama 1 — Canonical seçim
- Tek runtime entrypoint belirle (ör. `core/runtime.py`)
- Tek workflow executor belirle (diğeri deprecate)

### Aşama 2 — Boru hattı birleştirme
- `command_parser + task_decomposer` çıktısını doğrudan orchestrator/approval hattına bağla
- Interface’leri (CLI/Telegram/API) tek command bus’a yönlendir

### Aşama 3 — Temizlik/deprecation
- Çakışan dosyaları “deprecated” işaretle
- Arşiv dışı duplicate scriptleri kaldırma için migration checklist hazırla

### Aşama 4 — Done kriteri
Tek uçtan test:
- komut al → planla → onay/risk → uygula → raporla → state güncelle

---

## 8) Çalışma disiplini (zorunlu)
- Ana oturum: karar + özet
- İcra oturumu: kod + test + log
- Her icra sonunda ana oturuma kısa devir özeti
- Yeni durum değişikliği olunca önce bu dosya güncellenir

Cleanup durumu (2026-03-17): Runtime/workflow/intake çakışmaları archive taşımasıyla kapatıldı; aktif hat canonical set üzerinde çalışıyor.

---

## 9) Yeni gelen biri nereden başlamalı?
1. `docs/PROJECT_CANONICAL_STATE.md` (bu dosya)
2. `docs/GRAYWOLF_V2_CANONICAL_ARCHITECTURE.md`
3. `docs/DEPRECATION_MATRIX.md`
4. `docs/REPO_MAP.md`
5. `docs/ops/OPERATIONS.md`
6. `reports/release_candidate_handoff_2026-03-17.md`
