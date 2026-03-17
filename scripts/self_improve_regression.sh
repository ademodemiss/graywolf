#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adem/graywolf"
PY="/home/adem/.openclaw/workspace/.venv/bin/python"
LOG_DIR="$ROOT/logs"
OUT_MD="$LOG_DIR/self_improve_regression_latest.md"

mkdir -p "$LOG_DIR"

TESTS=(
  "tests/test_self_improve_tool.py"
  "tests/test_self_improve_orchestrator.py"
  "tests/test_replan_self_improve_scheduler.py"
  "tests/test_replan_self_improve_bridge.py"
  "tests/test_orchestrator_replan.py"
  "tests/test_approval_flow.py"
  "tests/test_approval_wait.py"
  "tests/test_approval_callback_router.py"
)

cd "$ROOT"
START_TS="$(date -Iseconds)"
set +e
OUTPUT="$($PY -m pytest -q "${TESTS[@]}" 2>&1)"
RC=$?
set -e
END_TS="$(date -Iseconds)"

STATUS="PASS"
if [[ $RC -ne 0 ]]; then
  STATUS="FAIL"
fi

{
  echo "# Self-Improve Regression Report"
  echo
  echo "- start: $START_TS"
  echo "- end: $END_TS"
  echo "- status: $STATUS"
  echo "- exit_code: $RC"
  echo
  echo "## Test scope"
  for t in "${TESTS[@]}"; do
    echo "- $t"
  done
  echo
  echo "## Pytest output"
  echo '```'
  echo "$OUTPUT"
  echo '```'
} > "$OUT_MD"

echo "$OUT_MD"
exit $RC
