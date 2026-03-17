#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adem/graywolf"
PY="/home/adem/.openclaw/workspace/.venv/bin/python"
MODE="${1:-daily}"

run_daily() {
  "$ROOT/scripts/operator_tasks.sh" all
  PYTHONPATH="$ROOT" "$PY" "$ROOT/scripts/queue_hygiene.py" --apply
  echo "ops_automation:daily:ok"
}

run_prerelease() {
  "$ROOT/scripts/release_precheck.sh"
  echo "ops_automation:prerelease:ok"
}

case "$MODE" in
  daily) run_daily ;;
  prerelease) run_prerelease ;;
  all)
    run_daily
    run_prerelease
    ;;
  *)
    echo "Usage: $0 {daily|prerelease|all}"
    exit 1
    ;;
esac
