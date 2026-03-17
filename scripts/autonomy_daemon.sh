#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adem/graywolf"
PY="/home/adem/.openclaw/workspace/.venv/bin/python"
PID_FILE="$ROOT/logs/autonomy_daemon.pid"
LOG_FILE="$ROOT/logs/autonomy_daemon.log"
INTERVAL_SECONDS="${AUTONOMY_INTERVAL_SECONDS:-120}"

mkdir -p "$ROOT/logs"

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid=$(cat "$PID_FILE" 2>/dev/null || true)
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

start() {
  if is_running; then
    echo "autonomy_daemon already running (pid=$(cat "$PID_FILE"))"
    exit 0
  fi

  nohup bash -lc '
    set -euo pipefail
    while true; do
      echo "[$(date -Is)] cycle:start"
      PYTHONPATH="/home/adem/graywolf" /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/scripts/run_autonomy_worker.py || true
      echo "[$(date -Is)] cycle:end sleep='"$INTERVAL_SECONDS"'s"
      sleep '"$INTERVAL_SECONDS"'
    done
  ' >> "$LOG_FILE" 2>&1 &

  echo $! > "$PID_FILE"
  echo "autonomy_daemon started (pid=$(cat "$PID_FILE"))"
}

stop() {
  if ! is_running; then
    echo "autonomy_daemon not running"
    rm -f "$PID_FILE"
    exit 0
  fi

  local pid
  pid=$(cat "$PID_FILE")
  kill "$pid" || true
  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" || true
  fi
  rm -f "$PID_FILE"
  echo "autonomy_daemon stopped"
}

status() {
  if is_running; then
    echo "autonomy_daemon running (pid=$(cat "$PID_FILE"))"
    echo "log: $LOG_FILE"
    tail -n 10 "$LOG_FILE" || true
  else
    echo "autonomy_daemon not running"
  fi
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  restart) stop || true; start ;;
  status) status ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
