from pathlib import Path

from core import assistant_context as ac


def test_assemble_assistant_context_clamps_to_max_budget(monkeypatch):
    monkeypatch.setenv('GW_CONTEXT_MAX_TOKENS', '1200')
    out = ac.assemble_assistant_context('merhaba', session_id='graywolf-assistant', source='test')
    assert out['max_tokens'] == 1200
    assert out['used_tokens'] <= out['max_tokens']


def test_assemble_assistant_context_respects_upper_budget(monkeypatch):
    monkeypatch.setenv('GW_CONTEXT_MAX_TOKENS', '999999')
    out = ac.assemble_assistant_context('iki sayıyı toplayan script yaz', session_id='graywolf-assistant', source='test')
    assert out['max_tokens'] == 100000
    assert out['used_tokens'] <= 100000


def test_select_relevant_long_memory_picks_related_items(monkeypatch, tmp_path):
    fake_root = tmp_path
    (fake_root / 'memory').mkdir(parents=True, exist_ok=True)
    p = fake_root / 'memory' / 'assistant_memory_summary.json'
    p.write_text(
        '{"items":[{"summary":"python script üretmeyi seviyor", "tags":["python"]}, {"summary":"hava durumu sohbetleri", "tags":["weather"]}]}'
    )

    monkeypatch.setattr(ac, 'ROOT', fake_root)
    monkeypatch.setattr(ac, 'LONG_MEMORY_FILE', p)

    selected = ac._select_relevant_long_memory('python script yaz')
    assert 'python script üretmeyi seviyor' in selected


def test_truncate_text_to_tokens():
    long_text = ' '.join(['kelime'] * 500)
    out = ac._truncate_text_to_tokens(long_text, 50)
    assert out
    assert ac.estimate_basic_tokens(out) <= 50


def test_context_blob_contains_prioritized_sections(monkeypatch):
    monkeypatch.setenv('GW_CONTEXT_MAX_TOKENS', '3000')
    out = ac.assemble_assistant_context('yardım eder misin', session_id='graywolf-assistant', source='test')
    blob = out['context_blob']
    assert '[system]' in blob
    assert '[active_message]' in blob
    assert '[short_term]' in blob
