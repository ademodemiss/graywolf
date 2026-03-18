from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path('/home/adem/graywolf/logs/interface_audit.log')


def write_audit(channel: str, action: str, status: str, detail: dict | None = None) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'channel': channel,
        'action': action,
        'status': status,
        'detail': detail or {},
    }
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
