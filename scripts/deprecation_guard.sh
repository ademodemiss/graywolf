#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Deprecated references that should not appear in active runtime code.
# Allow list: archive docs and this guard script itself.
PATTERN="core\.agent_loop|core\.service_runner|core\.full_autonomy|workflow_engine\.workflow_executor"

OUT=$(rg -n "$PATTERN" core monitor tools scripts workflows workflow_engine \
  -g '!core/agent_loop.py' \
  -g '!core/service_runner.py' \
  -g '!core/full_autonomy.py' \
  -g '!core/full_autonomy_controller.py' \
  -g '!workflow_engine/workflow_executor.py' \
  -g '!scripts/deprecation_guard.sh' 2>/dev/null || true)

if [[ -n "$OUT" ]]; then
  echo "[WARN] Deprecated runtime references found:"
  echo "$OUT"
  exit 1
fi

echo "[OK] No deprecated runtime references in active code paths."
