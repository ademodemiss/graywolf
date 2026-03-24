import io
import json
import sys
import types

from core import graywolf_cli as cli


class _FakeResp:
    def __init__(self, payload: dict):
        self._b = json.dumps(payload).encode('utf-8')

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_weather_reply_from_wttr_parses_payload(monkeypatch):
    payload = {
        'current_condition': [
            {
                'temp_C': '18',
                'FeelsLikeC': '16',
                'weatherDesc': [{'value': 'Partly cloudy'}],
            }
        ]
    }

    monkeypatch.setattr(cli.urllib.request, 'urlopen', lambda *_a, **_k: _FakeResp(payload))
    out = cli._weather_reply_from_wttr('Giresunda bugün hava durumu?', 'giresunda bugun hava durumu?')
    assert out is not None
    summary, next_step = out
    assert '18' in summary
    assert 'hissedilen' in summary.lower()
    assert next_step


def test_chat_answer_with_llm_returns_summary(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return '{"summary":"Python list, sıralı bir koleksiyondur.","next_step":"İstersen örnek vereyim."}'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._chat_answer_with_llm('Python list nedir?', 'ctx')
    assert out is not None
    assert 'koleksiyondur' in out[0]


def test_chat_answer_with_llm_plain_text_fallback(monkeypatch):
    class _FakeLLM:
        def generate_response(self, _prompt):
            return 'Python list, sıralı ve değiştirilebilir bir veri yapısıdır.'

    class _FakeRouter:
        def get(self):
            return _FakeLLM()

    monkeypatch.setitem(sys.modules, 'core.llm_router', types.SimpleNamespace(LLMRouter=_FakeRouter))
    out = cli._chat_answer_with_llm('Python list nedir?', 'ctx')
    assert out is not None
    assert 'veri yapısıdır' in out[0]
