import json
import subprocess
from pathlib import Path


ROOT = Path('/home/adem/graywolf')
CLI = ROOT / 'scripts' / 'graywolf'


def test_agent_plan_only_outputs_plan():
    p = subprocess.run(
        [str(CLI), 'agent', '--goal', 'bana bir program yap', '--plan-only', '--max-steps', '4'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['command'] == 'agent'
    assert payload['mode'] == 'plan_only'
    assert isinstance(payload.get('plan'), list)
    assert len(payload['plan']) == 4


def test_agent_empty_goal_errors():
    p = subprocess.run(
        [str(CLI), 'agent', '--goal', ''],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode != 0
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'error'
    assert 'empty_goal' in payload.get('errors', [])


def test_assistant_plan_only_outputs_goal_and_plan():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'sistemde sağlık kontrolü yap', '--plan-only', '--max-steps', '4'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['command'] == 'assistant'
    assert payload['mode'] == 'plan_only'
    assert isinstance(payload.get('goal'), str) and payload['goal'].strip()
    assert isinstance(payload.get('plan'), list)
    assert len(payload['plan']) == 4


def test_assistant_empty_message_errors():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', ''],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode != 0
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'error'
    assert 'empty_message' in payload.get('errors', [])
