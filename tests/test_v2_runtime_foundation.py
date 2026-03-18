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


def test_command_bus_policy_confirm_and_deny(tmp_path: Path):
    queue = tmp_path / 'queue'
    processed = tmp_path / 'processed'
    bus = CommandBus(str(queue), str(processed))

    confirm_env = bus.build_envelope(intent='deploy', payload={'goal': 'deploy now'}, source='pytest')
    confirm_out = bus.submit(confirm_env)
    assert confirm_out['status'] == 'confirm_required'
    assert confirm_out['policy']['decision'] == 'CONFIRM'

    deny_env = bus.build_envelope(intent='wipe_data', payload={'goal': 'wipe all'}, source='pytest')
    deny_out = bus.submit(deny_env)
    assert deny_out['status'] == 'denied'
    assert deny_out['policy']['decision'] == 'DENY'


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


def test_runtime_submit_command_confirm_required_exit0():
    cmd = [
        '/home/adem/.openclaw/workspace/.venv/bin/python',
        '-m',
        'core.runtime',
        'submit-command',
        '--session-id',
        'pytest-runtime',
        '--intent',
        'deploy',
        '--payload',
        '{"goal":"deploy production"}',
        '--source',
        'pytest',
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert p.returncode == 0

    payload = json.loads((p.stdout or '').strip().splitlines()[-1])
    assert payload['status'] == 'confirm_required'
    assert payload['policy']['decision'] == 'CONFIRM'
    assert payload['approval_request']['request_id'].startswith('APR-')


def test_runtime_approval_callback_grant_queues_pending():
    submit_cmd = [
        '/home/adem/.openclaw/workspace/.venv/bin/python',
        '-m',
        'core.runtime',
        'submit-command',
        '--session-id',
        'pytest-runtime',
        '--intent',
        'deploy',
        '--payload',
        '{"goal":"deploy with approval"}',
        '--source',
        'pytest',
    ]
    p1 = subprocess.run(submit_cmd, capture_output=True, text=True, check=False)
    assert p1.returncode == 0
    submit_payload = json.loads((p1.stdout or '').strip().splitlines()[-1])
    req_id = submit_payload['approval_request']['request_id']

    cb_cmd = [
        '/home/adem/.openclaw/workspace/.venv/bin/python',
        '-m',
        'core.runtime',
        'approval-callback',
        '--callback-data',
        f'approval.grant:{req_id}',
        '--actor',
        'pytest',
    ]
    p2 = subprocess.run(cb_cmd, capture_output=True, text=True, check=False)
    assert p2.returncode == 0

    cb_payload = json.loads((p2.stdout or '').strip().splitlines()[-1])
    assert cb_payload['status'] == 'ok'
    assert cb_payload['approval_request']['status'] == 'granted'
    assert cb_payload['queued']['status'] == 'queued'
