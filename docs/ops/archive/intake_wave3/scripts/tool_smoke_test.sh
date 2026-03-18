#!/usr/bin/env bash
set -euo pipefail

cd /home/adem/graywolf

PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python - <<'PY'
import datetime
import json
import os
import subprocess
from pathlib import Path

from tools import TOOL_REGISTRY
from tools.tool_guard import ToolGuard

log_file = Path('logs/tool_guard_smoke.log')
log_file.parent.mkdir(parents=True, exist_ok=True)

guard = ToolGuard(registry=TOOL_REGISTRY)
records = []

for descriptor in TOOL_REGISTRY.smoke_jobs():
    cmd = descriptor.smoke_test
    if not cmd:
        continue
    started = datetime.datetime.now(datetime.timezone.utc)
    try:
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            executable='/bin/bash',
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        status = 'ok'
        output = 'smoke test succeeded'
    except subprocess.CalledProcessError as exc:
        status = 'error'
        output = exc.stdout or exc.stderr or str(exc)
    entry = guard.record_tool_use(
        tool_name=descriptor.name,
        command=cmd,
        result_summary={
            'status': status,
            'output': output,
            'started_at': started.isoformat(),
        },
    )
    records.append(entry)

summary = {
    'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'records': records,
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
