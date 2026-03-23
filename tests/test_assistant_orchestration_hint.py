from core import graywolf_cli as cli


def test_orchestration_hint_chat_command_route():
    h = cli._orchestration_hint('chat_command')
    assert h['intent'] == 'chat_command'
    assert h['route'] == 'safe_execute'
    assert h['risk'] == 'low'


def test_orchestration_hint_invalid_intent_falls_back_execute():
    h = cli._orchestration_hint('unknown_intent')
    assert h['intent'] == 'execute'
    assert h['route'] == 'confirm_first'
