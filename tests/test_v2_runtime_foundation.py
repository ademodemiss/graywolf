import json
import subprocess
from pathlib import Path

from core.command_bus import CommandBus
from core.session_state import SessionStateStore


def test_command_bus_schema_and_submit(tmp_path: Path):
    queue = tmp_path / 'queue'
    processed = tmp_path / 'processed'
    bus = CommandBus(str(queue), str(processed))

    env = bus.build_envelope(intent='healthcheck', payload={'goal': 'test goal'}, source='pytest')
    out = bus.submit(env)

    assert out['status'] == 'queued'
    queued = Path(out['artifacts']['queued_task_file'])
    assert queued.exists()

    task = json.loads(queued.read_text(encoding='utf-8'))
    assert task['intent'] == 'healthcheck'
    assert task['source'] == 'pytest'


def test_session_state_store_roundtrip(tmp_path: Path):
    store = SessionStateStore(root=str(tmp_path / 'sessions'))
    sid = 'pytest-session'

    state = store.load(sid)
    assert state['session_id'] == sid

    updated = store.record(
        sid,
        command={'action': 'submit-command'},
        result={'status': 'queued'},
        active_task='TASK-1',
    )

    assert updated['last_command']['action'] == 'submit-command'
    assert updated['active_task'] == 'TASK-1'

    loaded = store.load(sid)
    assert loaded['history_count'] >= 1
    assert loaded['last_result']['status'] == 'queued'


def test_runtime_submit_command_cli():
    cmd = [
        '/home/adem/.openclaw/workspace/.venv/bin/python',
        '-m',
        'core.runtime',
        'submit-command',
        '--session-id',
        'pytest-runtime',
        '--intent',
        'healthcheck',
        '--payload',
        '{"goal":"pytest runtime command"}',
        '--source',
        'pytest',
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert p.returncode == 0

    payload = json.loads((p.stdout or '').strip().splitlines()[-1])
    assert payload['status'] == 'queued'
    assert payload['task']['task_id'].startswith('TASK-CMD-')
