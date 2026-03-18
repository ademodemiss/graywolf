# Post-Release 24h Monitoring Plan

Date: 2026-03-17
Baseline commit: 420405c
Branch: task/TASK-252-orchestrator-sleep-refactor

## 1) First 2 hours (every 30 min)
- Run: `bash scripts/daily_healthcheck.sh`
- Run: `bash scripts/operator_tasks.sh all`
- Check: `bash scripts/autonomy_daemon.sh status`
- Verify logs:
  - `logs/autonomy_daemon.log`
  - `logs/terminal.log`
  - `logs/replan_notifier.log`

## 2) Next 22 hours (every 2-4 hours)
- Run: `bash scripts/operator_tasks.sh all`
- Run: `bash scripts/self_improve_regression.sh`
- Confirm no growing critical errors in last 100 log lines

## 3) Alert conditions (immediate action)
- daemon stopped/crashed
- healthcheck fails
- operator_tasks returns non-ok
- regression script exits non-zero

## 4) Recovery quick actions
1. `bash scripts/autonomy_daemon.sh stop`
2. `bash scripts/autonomy_daemon.sh start`
3. `bash scripts/daily_healthcheck.sh`
4. If still failing: freeze changes + create incident note in `reports/`

## 5) Handoff message template
Devam bağlamı: Post-release 24s izleme aktif. Baseline=420405c. Son kontroller: daemon running, health/operator/regression PASS. Problem olursa recovery quick actions uygulanacak.
