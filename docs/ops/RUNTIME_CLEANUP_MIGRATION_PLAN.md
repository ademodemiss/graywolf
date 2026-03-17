# Runtime Cleanup & Migration Plan (Safe, No-Break)

_Last updated: 2026-03-17_

Amaç: Graywolf’ta çakışan runtime yollarını kırmadan temizlemek, deprecated parçaları güvenli şekilde arşive taşımak.

## Scope
- Deprecate set:
  - `core/full_autonomy.py`
  - `core/full_autonomy_controller.py`
  - `core/agent_loop.py`
  - `core/service_runner.py`
  - `workflow_engine/workflow_executor.py`
  - `agent/command_parser.py`
  - `agent/task_decomposer.py`
  - `agent/dispatcher.py`

- Canonical set (hedef):
  - `core/autonomous_loop.py`
  - `scripts/run_autonomy_worker.py`
  - `scripts/autonomy_daemon.sh`
  - `core/orchestrator.py`
  - `workflows/runner.py`

---

## Phase 1 — Referans temizliği (doküman + script import)
- [x] Canonical mimari/karar dosyaları yazıldı
- [x] `docs/ops/AUTONOMY_QUICKSTART.md` canonical komutlara taşındı
- [x] `scripts/simulate_approval_flow.py` canonical workflow importuna taşındı
- [x] `CHANGELOG.md` içindeki `core.agent_loop` örnekleri deprecated notuyla güncellendi
- [x] `docs/ops/archive/*` legacy referansları “historical only” etiketiyle bırakıldı

## Phase 2 — Deprecation guard (kod seviyesinde)
- [x] Deprecate dosyaların başına `DEPRECATED` başlığı + canonical yönlendirme eklendi
- [x] Yeni geliştirme/CI adımlarında deprecated dosyalara değişiklik uyarısı eklendi (`scripts/deprecation_guard.sh`)
- [x] `workflow_engine/workflow_executor.py` compatibility-only notu netleştirildi

## Phase 3 — Archive taşıma (kırmadan)
- [ ] `agent/*` dosyaları `archive/agent_legacy/` altına taşınacak
- [ ] Eski runtime dosyaları `archive/runtime_legacy/` altına taşınacak
- [ ] Taşıma sonrası `rg` ile kırık import taraması yapılacak
- [ ] Smoke doğrulama: worker + daemon + operator all + regression

## Phase 4 — Kapanış
- [x] `docs/DEPRECATION_MATRIX.md` final statüleri COMPLETE yapıldı
- [x] `docs/PROJECT_CANONICAL_STATE.md` “cleanup done” notu eklendi
- [x] Tek satırlık devir özeti güncellendi

---

## DoD (Definition of Done)
- Canonical hat dışında çalışan aktif runtime yolu kalmamalı.
- Deprecated dosyalar ya arşivde olmalı ya da açık yönlendirme notu taşımalı.
- Günlük operasyon komutları sadece canonical dosyalara dayanmalı.

## Kısa devir özeti (güncel)
Devam bağlamı: Runtime cleanup tamamlandı. Legacy runtime/workflow/intake dosyaları `archive/*_legacy/` altına taşındı; aktif canonical hat `core/autonomous_loop.py + scripts/run_autonomy_worker.py + scripts/autonomy_daemon.sh + core/orchestrator.py + workflows/runner.py`.
�nlük operasyon komutları sadece canonical dosyalara dayanmalı.
