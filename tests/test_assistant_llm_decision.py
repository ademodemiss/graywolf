import sys
import types

from core import graywolf_cli as cli


def test_infer_goal_llm_invalid_intent_falls_back_to_heuristic(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return '{"goal":"python script yaz","intent":"invalid_intent","confidence":0.95}'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_goal_with_llm('iki sayıyı toplayan script yaz')
    assert out['goal'] == 'python script yaz'
    assert out['intent'] == 'chat_command'
    assert out.get('trace', {}).get('llm_attempted') is True
    assert out.get('trace', {}).get('llm_parsed') is True


def test_infer_goal_llm_codefence_json_parsed(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return '```json\n{"goal":"saglik kontrolu yap","intent":"healthcheck","confidence":0.8}\n```'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_goal_with_llm('sistemi kontrol et')
    assert out['goal'] == 'saglik kontrolu yap'
    assert out['intent'] == 'healthcheck'
    assert out['provider'] == 'llm'
    assert out.get('trace', {}).get('llm_used') is True


def test_infer_goal_llm_disabled_env_keeps_heuristic(monkeypatch):
    monkeypatch.setenv('GW_ASSISTANT_LLM', '0')

    class _FakeLLM:
        def generate_response(self, _prompt):
            raise AssertionError('LLM must not be called when disabled')

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_goal_with_llm('iki sayıyı toplayan script yaz')
    assert out['provider'] == 'heuristic'
    assert out['intent'] == 'chat_command'
    assert out.get('trace', {}).get('fallback_reason') == 'llm_disabled'


def test_infer_triage_llm_invalid_json_returns_none(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return 'no-json'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._infer_triage_with_llm('bu nedir?')
    assert out is None
