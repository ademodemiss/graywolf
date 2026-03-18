# Runtime Cleanup Completion Report — 2026-03-17

## Objective
Graywolf runtime/workflow/intake çakışmalarını kapatıp canonical hattı tekleştirmek.

## Canonical Active Path
- `core/autonomous_loop.py`
- `scripts/run_autonomy_worker.py`
- `scripts/autonomy_daemon.sh`
- `core/orchestrator.py`
- `workflows/runner.py`

## Archived Legacy Paths
- `archive/runtime_legacy/{full_autonomy.py,full_autonomy_controller.py,agent_loop.py,service_runner.py}`
- `archive/workflow_legacy/workflow_executor.py`
- `archive/agent_legacy/{command_parser.py,task_decomposer.py,dispatcher.py}`

## Documentation Updated
- `docs/PROJECT_CANONICAL_STATE.md`
- `docs/GRAYWOLF_V2_CANONICAL_ARCHITECTURE.md`
- `docs/DEPRECATION_MATRIX.md`
- `docs/ops/RUNTIME_CLEANUP_MIGRATION_PLAN.md`
- `docs/ops/AUTONOMY_QUICKSTART.md`
- `docs/ops/archive/{CURRENT_STATE.md,NEXT_ACTION.md,RELEASE_CHECKLIST.md}`
- `CHANGELOG.md`

## Validation
- `scripts/deprecation_guard.sh` => OK
- `scripts/operator_tasks.sh all` => repo:ok / health:ok / risk:ok
- `scripts/self_improve_regression.sh` => PASS
- `scripts/autonomy_daemon.sh status` => running

## Outcome
Cleanup hedefi tamamlandı. Aktif ürün akışı canonical set üzerinde çalışıyor; legacy yollar archive altında korunuyor.
