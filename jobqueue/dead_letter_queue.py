import datetime
import json
from pathlib import Path

DLQ_DB = Path('/home/adem/graywolf/queue/dead_letter.json')


def _load() -> list[dict]:
    if not DLQ_DB.exists():
        return []
    try:
        return json.loads(DLQ_DB.read_text(encoding='utf-8'))
    except Exception:
        return []


def _save(rows: list[dict]):
    DLQ_DB.parent.mkdir(parents=True, exist_ok=True)
    DLQ_DB.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')


def push_dead_letter(task: dict, reason: str) -> dict:
    rows = _load()
    row = {
        'task_id': task.get('task_id'),
        'command': task.get('command'),
        'attempts': int(task.get('attempts', 0)),
        'reason': reason,
        'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    rows.append(row)
    _save(rows)
    return row


def get_dead_letters() -> list[dict]:
    return _load()


if __name__ == '__main__':
    print(json.dumps({'status': 'ok', 'count': len(get_dead_letters())}, ensure_ascii=False))
