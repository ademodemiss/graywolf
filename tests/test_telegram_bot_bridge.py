from telegram_bot import _format_result, split_chunks


def test_split_chunks_empty_returns_placeholder():
    assert split_chunks('') == ['(çıktı yok)']


def test_split_chunks_respects_limit():
    text = 'a' * 9000
    chunks = split_chunks(text, limit=4000)
    assert len(chunks) == 3
    assert all(len(c) <= 4000 for c in chunks)


def test_format_result_includes_mode_triage_and_next_step():
    res = {
        'json': {
            'status': 'ok',
            'command': 'assistant',
            'mode': 'chat',
            'triage': {'kind': 'chat', 'reason': 'chat_question'},
            'ux': {'summary': 'Sorunu sohbet sorusu olarak algıladım.', 'next_step': 'Detay sor.'},
        }
    }
    out = _format_result(res)
    assert 'mode: chat' in out
    assert 'triage: chat (chat_question)' in out
    assert 'next_step: Detay sor.' in out


def test_format_result_includes_errors_when_present():
    res = {'json': {'status': 'error', 'command': 'assistant', 'errors': ['empty_message']}}
    out = _format_result(res)
    assert 'errors: empty_message' in out
