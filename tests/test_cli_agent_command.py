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
    assert isinstance(payload.get('orchestration_hint'), dict)
    assert payload['orchestration_hint'].get('intent') in {'healthcheck', 'analyze', 'execute', 'deploy', 'chat_command'}
    contract = payload.get('assistant_output') or {}
    assert contract.get('contract_version') == 'v1'
    assert contract.get('mode') == 'plan_only'
    assert isinstance((contract.get('response') or {}).get('summary'), str)
    meta = contract.get('tool_payload_meta') or {}
    assert meta.get('intent') in {'healthcheck', 'analyze', 'execute', 'deploy', 'chat_command'}
    assert meta.get('session_id') == 'graywolf-assistant'


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


def test_assistant_script_request_prefers_chat_command_intent():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'iki sayıyı toplayan basit bir python script yaz', '--plan-only', '--max-steps', '3'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['intent'] == 'chat_command'
    hint = payload.get('orchestration_hint') or {}
    assert hint.get('route') == 'safe_execute'
    assert hint.get('risk') == 'low'


def test_assistant_high_risk_phrase_keeps_deploy_intent():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'production deploy script yaz', '--plan-only', '--max-steps', '3'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['intent'] == 'deploy'


def test_assistant_merhaba_goes_chat_mode():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'Merhaba'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'chat'
    contract = payload.get('assistant_output') or {}
    assert contract.get('contract_version') == 'v1'
    assert contract.get('mode') == 'chat'
    meta = contract.get('tool_payload_meta') or {}
    assert meta.get('triage_kind') == 'chat'


def test_assistant_nasilsin_goes_chat_mode():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'Nasılsın'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'chat'


def test_assistant_script_message_is_task_path_not_chat_mode():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'iki sayıyı toplayan script yaz', '--plan-only', '--max-steps', '3'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'plan_only'
    assert payload.get('triage', {}).get('kind') == 'task'


def test_assistant_sen_kimsin_goes_chat_identity_not_unclear():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'SEN KİMSİN'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'chat'
    assert payload.get('triage', {}).get('reason') != 'uncertain_clarify'
    assert 'graywolf' in payload.get('ux', {}).get('summary', '').lower()


def test_assistant_weather_question_goes_chat_not_unclear():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'GİRESUN HAVA DURUMU NEDİR ?'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'chat'
    assert payload.get('triage', {}).get('reason') == 'chat_pattern'
    summary = payload.get('ux', {}).get('summary', '').lower()
    assert ('hava durumu' in summary) or ('°c' in summary) or ('su an' in summary)


def test_assistant_nasilsin_goes_chat_not_unclear():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'Nasılsın'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'chat'
    assert payload.get('triage', {}).get('reason') == 'chat_pattern'


def test_assistant_generic_question_goes_chat_question_mode():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'Python list nedir?'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'chat'
    assert payload.get('triage', {}).get('reason') == 'chat_question'
    assert 'sohbet sorusu' in payload.get('ux', {}).get('summary', '').lower()


def test_assistant_high_risk_deploy_phrase_routes_task_not_unclear():
    p = subprocess.run(
        [str(CLI), 'assistant', '--message', 'productiona deploy et', '--plan-only', '--max-steps', '1'],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    payload = json.loads(p.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'plan_only'
    assert payload.get('triage', {}).get('kind') == 'task'
    assert payload.get('triage', {}).get('reason') == 'task_pattern'
