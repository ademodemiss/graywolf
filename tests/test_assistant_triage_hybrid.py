import sys
import types

import argparse

from core import graywolf_cli as cli


def test_triage_keeps_rule_based_chat_without_llm(monkeypatch):
    called = {'v': False}

    def _fake(_message):
        called['v'] = True
        return {'kind': 'task', 'confidence': 0.99}

    monkeypatch.setattr(cli, '_infer_triage_with_llm', _fake)
    kind, reason = cli._triage_message_kind('Merhaba')
    assert kind == 'chat'
    assert reason == 'chat_pattern'
    assert called['v'] is False


def test_triage_keeps_rule_based_task_without_llm(monkeypatch):
    called = {'v': False}

    def _fake(_message):
        called['v'] = True
        return {'kind': 'chat', 'confidence': 0.99}

    monkeypatch.setattr(cli, '_infer_triage_with_llm', _fake)
    kind, reason = cli._triage_message_kind('iki sayıyı toplayan script yaz')
    assert kind == 'task'
    assert reason == 'task_pattern'
    assert called['v'] is False


def test_triage_uncertain_uses_llm_chat(monkeypatch):
    monkeypatch.setattr(cli, '_infer_triage_with_llm', lambda _m: {'kind': 'chat', 'confidence': 0.88})
    kind, reason = cli._triage_message_kind('bugün hava nasıl')
    assert kind == 'chat'
    assert reason == 'llm_chat'


def test_triage_uncertain_uses_llm_task_high_confidence(monkeypatch):
    monkeypatch.setattr(cli, '_infer_triage_with_llm', lambda _m: {'kind': 'task', 'confidence': 0.91})
    kind, reason = cli._triage_message_kind('logları toparlayıp bir özet geç')
    assert kind == 'task'
    assert reason == 'llm_task'


def test_triage_uncertain_llm_unclear_kept_unclear(monkeypatch):
    monkeypatch.setattr(cli, '_infer_triage_with_llm', lambda _m: {'kind': 'unclear', 'confidence': 0.75})
    kind, reason = cli._triage_message_kind('bakar mısın bir şeye')
    assert kind == 'unclear'
    assert reason == 'llm_unclear'


def test_llm_triage_invalid_json_falls_back(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return 'not-json-at-all'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_triage_with_llm('kararsız bir mesaj')
    assert out is None


def test_llm_triage_exception_falls_back(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            raise TimeoutError('timeout')

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_triage_with_llm('kararsız bir mesaj')
    assert out is None


def test_llm_triage_invalid_enum_kind_falls_back(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return '{"kind":"other","confidence":0.99,"reason":"x"}'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_triage_with_llm('kararsız bir mesaj')
    assert out is None


def test_cmd_assistant_unclear_does_not_trigger_task_path(monkeypatch):
    monkeypatch.setattr(cli, '_triage_message_kind', lambda _m: ('unclear', 'llm_unclear'))

    def _should_not_run(_m):
        raise AssertionError('task path should not run for unclear triage')

    monkeypatch.setattr(cli, '_infer_goal_with_llm', _should_not_run)
    args = argparse.Namespace(message='bakar mısın', max_steps=3, source='test', session_id='s', plan_only=False)
    payload = cli.cmd_assistant(args)
    assert payload['status'] == 'ok'
    assert payload['mode'] == 'chat'
    assert payload.get('triage', {}).get('kind') == 'unclear'
