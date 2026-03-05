import json
from pathlib import Path

QUEUE_DB = Path('/home/adem/graywolf/queue/tasks.json')


def load_tasks() -> list[dict]:
    if not QUEUE_DB.exists():
        return []
    try:
        return json.loads(QUEUE_DB.read_text(encoding='utf-8'))
    except Exception:
        return []


def save_tasks(tasks: list[dict]):
    QUEUE_DB.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_DB.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding='utf-8')
