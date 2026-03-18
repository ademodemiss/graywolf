#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

QUEUE = Path('/home/adem/graywolf/tasks/queue')
QUEUE.mkdir(parents=True, exist_ok=True)

TASKS = [
    {
        "task_id": "AUTO-REAL-001",
        "goal": "Projedeki son commitleri kısa özetle ve bir durum notu üret.",
        "priority": "normal"
    },
    {
        "task_id": "AUTO-REAL-002",
        "goal": "dashboard test komutunu çalıştır ve sonuç raporu yaz.",
        "priority": "normal"
    }
]

for t in TASKS:
    t["status"] = "queued"
    t["queued_at"] = datetime.now().isoformat()
    p = QUEUE / f"{t['task_id']}.json"
    p.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
    print(f"queued: {p}")
