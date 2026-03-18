#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_PY="$HOME/.openclaw/workspace/.venv/bin/python"
if [[ -x "$DEFAULT_PY" ]]; then
  PY="$DEFAULT_PY"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
else
  PY="python3"
fi
LOG="$ROOT/reports/release_precheck_latest.md"

mkdir -p "$ROOT/reports"

run_step() {
  local name="$1"
  local cmd="$2"
  echo "## $name" >> "$LOG"
  echo "- cmd: \`$cmd\`" >> "$LOG"
  set +e
  out=$(bash -lc "$cmd" 2>&1)
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "- status: PASS" >> "$LOG"
  else
    echo "- status: FAIL" >> "$LOG"
  fi
  echo '```' >> "$LOG"
  echo "$out" >> "$LOG"
  echo '```' >> "$LOG"
  echo >> "$LOG"
  return $rc
}

: > "$LOG"
echo "# Release Precheck Report" >> "$LOG"
echo "- ts: $(date -Iseconds)" >> "$LOG"
echo >> "$LOG"

run_step "Deprecation Guard" "$ROOT/scripts/deprecation_guard.sh"
run_step "Operator Tasks (all)" "$ROOT/scripts/operator_tasks.sh all"
run_step "E2E Canonical Acceptance" "PYTHONPATH=$ROOT $PY $ROOT/scripts/e2e_canonical_acceptance.py"

echo "release_precheck: PASS"
echo "$LOG"
