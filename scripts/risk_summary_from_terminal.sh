#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$ROOT/logs/terminal.log"
OUT_FILE="$ROOT/logs/real_task_risk_summary.md"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "# Risk Summary\n\nTerminal log bulunamadı: $LOG_FILE" > "$OUT_FILE"
  exit 0
fi

LAST20=$(tail -n 20 "$LOG_FILE")
WARN_COUNT=$(echo "$LAST20" | grep -Eci '"decision":\s*"CONFIRM"|"status":\s*"needs_confirmation"|"status":\s*"timeout"|"status":\s*"error"' || true)
DENY_COUNT=$(echo "$LAST20" | grep -Eci '"decision":\s*"DENY"|blocked by policy' || true)

{
  echo "# Terminal Risk Summary"
  echo
  echo "- İncelenen kayıt: son 20 satır"
  echo "- Warning/needs_confirmation/error/timeout: $WARN_COUNT"
  echo "- Deny/blocked: $DENY_COUNT"
  echo
  echo "## Son 20 satır"
  echo '```json'
  echo "$LAST20"
  echo '```'
} > "$OUT_FILE"

echo "written:$OUT_FILE"
