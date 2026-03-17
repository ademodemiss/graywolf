#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/adem/graywolf"
PY="/home/adem/.openclaw/workspace/.venv/bin/python"
QUEUE="$ROOT/tasks/queue"
PROCESSED="$ROOT/tasks/processed"
REPORT="$ROOT/logs/three_tasks_summary.md"

mkdir -p "$QUEUE" "$PROCESSED" "$ROOT/logs"

TS=$(date +%Y%m%d%H%M%S)
T1="AUTO-BATCH-${TS}-101"
T2="AUTO-BATCH-${TS}-102"
T3="AUTO-BATCH-${TS}-103"

$PY - <<'PY'
import json, os
from datetime import datetime
from pathlib import Path

root=Path('/home/adem/graywolf')
queue=root/'tasks'/'queue'
queue.mkdir(parents=True,exist_ok=True)

ts=os.popen('date +%Y%m%d%H%M%S').read().strip()
tasks=[
 (f"AUTO-BATCH-{ts}-101","Bugünkü repo durumunu kısa özetle ve logs/real_task_repo_status.md dosyasına yaz."),
 (f"AUTO-BATCH-{ts}-102","Daily healthcheck çalıştır ve sonucu logs/real_task_healthcheck.md dosyasına yaz."),
 (f"AUTO-BATCH-{ts}-103","Son 20 terminal log satırını incele, risk/uyarı özetini logs/real_task_risk_summary.md dosyasına yaz. Tercihen /home/adem/graywolf/scripts/risk_summary_from_terminal.sh kullan.")
]
for tid,goal in tasks:
    t={"task_id":tid,"goal":goal,"priority":"high","status":"queued","queued_at":datetime.now().isoformat()}
    (queue/f"{tid}.json").write_text(json.dumps(t,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    print(tid)
PY

for _ in 1 2 3; do
  PYTHONPATH="$ROOT" "$PY" "$ROOT/scripts/run_autonomy_worker.py" >/dev/null || true
done

$PY - <<'PY'
import glob, json
from pathlib import Path
from datetime import datetime

root=Path('/home/adem/graywolf')
processed=root/'tasks'/'processed'
logs=root/'logs'
report=logs/'three_tasks_summary.md'

files=sorted(glob.glob(str(processed/'AUTO-BATCH-*-10[123].json')))[-3:]
lines=[f"# Three Real Tasks Summary ({datetime.now().isoformat()})",""]

if not files:
    lines.append("- No processed batch files found.")
else:
    for p in files:
        d=json.load(open(p))
        tid=d.get('task_id')
        st=d.get('status')
        wf=d.get('result',{}).get('status')
        lines.append(f"- {tid}: status={st}, workflow={wf}")

lines += ["","## Output files","- logs/real_task_repo_status.md","- logs/real_task_healthcheck.md","- logs/real_task_risk_summary.md",""]

report.write_text("\n".join(lines)+"\n",encoding='utf-8')
print(report)
PY

echo "DONE: $REPORT"
