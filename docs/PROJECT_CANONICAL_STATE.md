# Graywolf Canonical Project State

_Last updated: 2026-03-18_

Bu dosya Graywolf v1.0 için tek teknik gerçek durum kaynağıdır.

## 1) Ürün Kimliği
Graywolf, **assistant-first deneyim + güvenli execution runtime** modelinde çalışan stateful bir AI operasyon asistanıdır.

## 2) Aktif V1.0 Omurga (KEEP)
- Runtime: `core/runtime.py`
- Command bus/policy: `core/command_bus.py`, `policies/intent_policy.py`, `policies/shell_policy.py`
- Session/queue: `core/session_state.py`, `core/task_queue.py`
- Worker loop: `core/autonomous_loop.py`, `scripts/run_autonomy_worker.py`, `scripts/autonomy_daemon.sh`
- Orchestrator/execution: `core/orchestrator.py`, `workflows/runner.py`
- Approval bridge: `core/approval.py`, `monitor/approval_callback_router.py`
- Observability gates: `scripts/release_precheck.sh`, `scripts/operator_tasks.sh`
- CLI: `core/graywolf_cli.py`, `scripts/graywolf`
- Assistant intake chain: `agent/command_parser.py`, `agent/task_decomposer.py`, `agent/dispatcher.py`

## 3) Çalışma Sözleşmesi
- intent -> policy -> queue -> execute -> report
- Policy kararları:
  - `ALLOW` -> `queued`
  - `CONFIRM` -> `confirm_required`
  - `DENY` -> `denied`
- `confirm_required` exit code başarısızlık sayılmaz (operasyonel bekleme durumu)

## 4) V1.0 Dışına Alınanlar (Archive/Deferred)
- phase plan/monitoring dokümanları (`docs/ops/archive/intake_wave2/...`)
- verification fixture/tooling (`docs/ops/archive/intake_wave2/verification/...`)
- deneysel/çekirdek dışı artefaktlar

## 5) Gerçek Durum
- Runtime spine çalışır
- Precheck geçer
- CI release-precheck green
- main/task/origin senkron (closure turunda doğrulandı)

## 6) Bilinçli Ertelemeler
- Multi-agent kapsamı
- Ürün çekirdeğine doğrudan katkısı olmayan deneysel katmanlar
- Büyük refactorlar (v1.0 sonrası)
