# Graywolf v2 Freeze Release Note — 2026-03-17

## Release Summary
Graywolf, bu tarih itibarıyla **kendi runtime’ı olan tekil operasyon sistemi** hedefinin v2 foundation aşamasını tamamlamıştır.

- Runtime kernel: `core/runtime.py`
- Unified command bus: `core/command_bus.py`
- Session state layer: `core/session_state.py`
- Interface adapters: `adapters/interface/*`
- E2E canonical acceptance: `scripts/e2e_canonical_acceptance.py`

## Canonical Active Path
- `core/autonomous_loop.py`
- `scripts/run_autonomy_worker.py`
- `scripts/autonomy_daemon.sh`
- `core/orchestrator.py`
- `workflows/runner.py`

## Release Gates
Zorunlu precheck:
- `scripts/release_precheck.sh`
  1) `scripts/deprecation_guard.sh`
  2) `scripts/operator_tasks.sh all`
  3) `scripts/e2e_canonical_acceptance.py`

## Queue Hygiene
- `scripts/queue_hygiene.py --apply`
- Test/acceptance artefactları `tasks/processed_test` / `tasks/queue_test` altına ayrılır.

## Runtime Observability
`core.runtime status` artık şunları içerir:
- approval health + callback özeti
- session restore/state özeti
- queue depth + son 5 queued/processed task

## Evidence
- `reports/e2e_canonical_acceptance_latest.md` (PASS)
- `reports/release_precheck_latest.md` (PASS)
- `reports/runtime_cleanup_completion_2026-03-17.md`

## Decision
Bu sürüm **v2 foundation freeze** olarak kabul edildi.
Bir sonraki faz: v2 hardening sprint (stabilizasyon, CI entegrasyonu, üretim operasyon otomasyonu).
