#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adem/graywolf"
PY="/home/adem/.openclaw/workspace/.venv/bin/python"

ok() { echo "[OK] $1"; }
step() { echo "\n==> $1"; }

step "Dashboard test"
$PY "$ROOT/dashboard/server.py" --test >/tmp/graywolf_dashboard_test.out
if grep -q "dashboard_test_ok" /tmp/graywolf_dashboard_test.out; then
  ok "dashboard_test_ok"
else
  echo "[FAIL] dashboard test failed"
  cat /tmp/graywolf_dashboard_test.out
  exit 1
fi

step "Replan health reporter"
PYTHONPATH="$ROOT" $PY "$ROOT/monitor/replan_health_reporter.py" --telegram | tee /tmp/graywolf_replan_health.out >/dev/null
ok "replan health reporter ran"

step "Trend watcher dry-run"
PYTHONPATH="$ROOT" $PY "$ROOT/monitor/learning_recovery_trend.py" --dry-run | tee /tmp/graywolf_trend_dryrun.out >/dev/null
ok "trend dry-run ran"

step "Critical pytest subset"
cd "$ROOT"
$PY -m pytest -q \
  tests/test_replan_health_reporter.py \
  tests/test_replan_self_improve_bridge.py \
  tests/test_replan_self_improve_scheduler.py \
  tests/test_recovery_dispatcher.py \
  tests/test_approval_health.py \
  tests/test_approval_callback_router.py \
  tests/provider_validation_test.py \
  tests/provider_validation_outlook_test.py
ok "critical tests passed"

echo "\n✅ DAILY HEALTHCHECK PASSED"
