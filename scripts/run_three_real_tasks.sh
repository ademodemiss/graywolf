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

task_outputs={
    '101': root/'logs'/'real_task_repo_status.md',
    '102': root/'logs'/'real_task_healthcheck.md',
    '103': root/'logs'/'real_task_risk_summary.md',
}

scored=[]

def score_task(status, workflow_status, output_path):
    score=0
    if status == 'completed':
        score += 40
    if workflow_status in {'completed', 'success'}:
        score += 25
    if output_path.exists():
        score += 25
        if output_path.stat().st_size > 20:
            score += 10
    return min(score, 100)

if not files:
    lines.append("- No processed batch files found.")
else:
    for p in files:
        d=json.load(open(p))
        tid=d.get('task_id','')
        st=d.get('status')
        wf=d.get('result',{}).get('status')
        suffix=tid[-3:]
        out=task_outputs.get(suffix, root/'logs'/'unknown_output.md')
        quality_score=score_task(st, wf, out)
        scored.append(quality_score)
        lines.append(f"- {tid}: status={st}, workflow={wf}, quality_score={quality_score}/100")

if scored:
    avg=sum(scored)/len(scored)
    lines += ["", f"## Quality scoring", f"- average_quality_score: {avg:.1f}/100"]

lines += ["","## Output files","- logs/real_task_repo_status.md","- logs/real_task_healthcheck.md","- logs/real_task_risk_summary.md",""]

report.write_text("\n".join(lines)+"\n",encoding='utf-8')
print(report)
PY

echo "DONE: $REPORT"
