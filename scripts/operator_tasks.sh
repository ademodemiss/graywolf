#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:-all}"
mkdir -p "$ROOT/logs"

run_repo() {
  {
    echo "Repo Durumu Özeti ($(date +%Y-%m-%d\ %H:%M))" > "$ROOT/logs/real_task_repo_status.md"
    echo -e "\n--- Mevcut Değişiklikler ---\n" >> "$ROOT/logs/real_task_repo_status.md"
    git -C "$ROOT" status -s >> "$ROOT/logs/real_task_repo_status.md"
    echo -e "\n--- Son Commit ---\n" >> "$ROOT/logs/real_task_repo_status.md"
    git -C "$ROOT" log -1 --pretty=format:"%h - %an, %ar - %s" >> "$ROOT/logs/real_task_repo_status.md"
  }
  echo "repo:ok"
}

run_health() {
  "$ROOT/scripts/daily_healthcheck.sh" > "$ROOT/logs/real_task_healthcheck.md" 2>&1
  echo "health:ok"
}

run_risk() {
  "$ROOT/scripts/risk_summary_from_terminal.sh" >/dev/null
  echo "risk:ok"
}

case "$mode" in
  repo) run_repo ;;
  health)
    if [[ "${CI:-}" == "true" ]]; then
      echo "health:skipped(ci)"
    else
      run_health
    fi
    ;;
  risk)
    if [[ "${CI:-}" == "true" ]]; then
      echo "risk:skipped(ci)"
    else
      run_risk
    fi
    ;;
  all)
    run_repo
    if [[ "${CI:-}" == "true" ]]; then
      echo "health:skipped(ci)"
      echo "risk:skipped(ci)"
    else
      run_health
      run_risk
    fi
    ;;
  *)
    echo "Usage: $0 {repo|health|risk|all}"
    exit 1
    ;;
esac

echo "done:$mode"
