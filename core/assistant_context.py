from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from adapters.llm import estimate_basic_tokens

ROOT = Path('/home/adem/graywolf')
SESSIONS_DIR = ROOT / 'sessions'
AGENT_RUNS_DIR = SESSIONS_DIR / 'agent_runs'
PENDING_APPROVALS_FILE = SESSIONS_DIR / 'pending_approvals.json'
LONG_MEMORY_FILE = ROOT / 'memory' / 'assistant_memory_summary.json'

DEFAULT_MAX_CONTEXT_TOKENS = 100_000


def _safe_load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default
    return default


def _token_overlap_score(query: str, text: str) -> int:
    q = {w.strip('.,:;!?()[]{}"\'').lower() for w in (query or '').split() if len(w.strip()) >= 3}
    t = {w.strip('.,:;!?()[]{}"\'').lower() for w in (text or '').split() if len(w.strip()) >= 3}
    if not q or not t:
        return 0
    return len(q & t)


def _truncate_text_to_tokens(text: str, max_tokens: int) -> str:
    if max_tokens <= 0:
        return ''
    if estimate_basic_tokens(text) <= max_tokens:
        return text

    words = text.split()
    if not words:
        return ''

    low, high = 1, len(words)
    best = ''
    while low <= high:
        mid = (low + high) // 2
        candidate = ' '.join(words[:mid])
        if estimate_basic_tokens(candidate) <= max_tokens:
            best = candidate
            low = mid + 1
        else:
            high = mid - 1
    out = (best + ' …').strip()
    while out and estimate_basic_tokens(out) > max_tokens:
        parts = out.split()
        if len(parts) <= 1:
            return ''
        out = ' '.join(parts[:-2]).strip()
        if out:
            out = (out + ' …').strip()
    return out


def _summarize_session_state(session_id: str) -> str:
    state = _safe_load_json(SESSIONS_DIR / f'{session_id}.json', {})
    if not isinstance(state, dict) or not state:
        return ''

    last_command = state.get('last_command') or {}
    last_result = state.get('last_result') or {}
    lines = [
        f"session_id={state.get('session_id', session_id)}",
        f"history_count={state.get('history_count', 0)}",
        f"active_task={state.get('active_task')}",
    ]
    if isinstance(last_command, dict):
        lines.append(f"last_intent={last_command.get('intent')}")
        lines.append(f"last_source={last_command.get('source')}")
    if isinstance(last_result, dict):
        lines.append(f"last_status={last_result.get('status')}")
    return '; '.join(str(x) for x in lines if x is not None)


def _summarize_pending_approvals(session_id: str, limit: int = 3) -> str:
    data = _safe_load_json(PENDING_APPROVALS_FILE, {})
    items = []
    if isinstance(data, dict):
        raw = data.get('pending')
        if isinstance(raw, list):
            items = raw
    if not items:
        return ''

    filtered = [x for x in items if isinstance(x, dict) and (x.get('session_id') == session_id)]
    if not filtered:
        return ''

    tail = filtered[-limit:]
    parts = []
    for x in tail:
        rid = x.get('request_id')
        status = x.get('status')
        reason = ((x.get('policy') or {}).get('reason') if isinstance(x.get('policy'), dict) else None)
        cmd = x.get('command') if isinstance(x.get('command'), dict) else {}
        intent = cmd.get('intent')
        parts.append(f"{rid}:{status}:intent={intent}:reason={reason}")
    return ' | '.join(parts)


def _summarize_recent_runs(session_id: str, limit: int = 2) -> str:
    if not AGENT_RUNS_DIR.exists():
        return ''

    run_files = sorted(AGENT_RUNS_DIR.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    parts: list[str] = []
    for p in run_files:
        if len(parts) >= limit:
            break
        data = _safe_load_json(p, {})
        if not isinstance(data, dict):
            continue
        if data.get('session_id') != session_id:
            continue
        run_id = data.get('run_id') or p.stem
        status = data.get('status')
        goal = (data.get('goal') or '')
        parts.append(f"run={run_id};status={status};goal={goal[:120]}")
    return ' | '.join(parts)


def _select_relevant_long_memory(message: str, limit: int = 3) -> str:
    data = _safe_load_json(LONG_MEMORY_FILE, {})
    items = []
    if isinstance(data, dict):
        raw = data.get('items')
        if isinstance(raw, list):
            items = raw
    if not items:
        return ''

    scored: list[tuple[int, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        text = str(item.get('summary') or '').strip()
        if not text:
            continue
        score = _token_overlap_score(message, text)
        if score <= 0:
            continue
        tags = item.get('tags') if isinstance(item.get('tags'), list) else []
        tag_txt = ','.join(str(t) for t in tags[:5])
        scored.append((score, f"summary={text};tags={tag_txt}"))

    if not scored:
        return ''

    scored.sort(key=lambda x: x[0], reverse=True)
    return ' | '.join(text for _, text in scored[:limit])


def _max_context_tokens() -> int:
    raw = os.getenv('GW_CONTEXT_MAX_TOKENS', str(DEFAULT_MAX_CONTEXT_TOKENS)).strip()
    try:
        parsed = int(raw)
    except Exception:
        parsed = DEFAULT_MAX_CONTEXT_TOKENS
    return max(1024, min(parsed, DEFAULT_MAX_CONTEXT_TOKENS))


def assemble_assistant_context(message: str, session_id: str, source: str = 'graywolf-assistant') -> dict:
    max_tokens = _max_context_tokens()

    system_text = (
        'Assistant context policy: keep context concise, include only relevant memory summaries, '
        'avoid raw long history dumps, respect conservative task escalation.'
    )
    message_text = (message or '').strip()
    short_term = {
        'session': _summarize_session_state(session_id),
        'approvals': _summarize_pending_approvals(session_id),
        'runs': _summarize_recent_runs(session_id),
    }
    long_term = {
        'memory_summary': _select_relevant_long_memory(message_text),
    }
    extras = {
        'source': source,
    }

    sections = [
        ('system', system_text),
        ('active_message', message_text),
        ('short_term', json.dumps(short_term, ensure_ascii=False)),
        ('long_term', json.dumps(long_term, ensure_ascii=False)),
        ('extras', json.dumps(extras, ensure_ascii=False)),
    ]

    chosen: list[tuple[str, str, int]] = []
    used = 0

    for name, text in sections:
        if not text:
            continue
        remaining = max_tokens - used
        if remaining <= 0:
            break

        tok = estimate_basic_tokens(text)
        final_text = text
        final_tok = tok
        if tok > remaining:
            final_text = _truncate_text_to_tokens(text, remaining)
            final_tok = estimate_basic_tokens(final_text)

        if final_text:
            chosen.append((name, final_text, final_tok))
            used += final_tok

    context_blob = '\n'.join([f'[{name}] {text}' for name, text, _ in chosen])

    return {
        'max_tokens': max_tokens,
        'used_tokens': min(used, max_tokens),
        'context_blob': context_blob,
        'sections': [{'name': n, 'tokens': t} for n, _, t in chosen],
        'memory_summary': {
            'short_term': short_term,
            'long_term': long_term,
        },
    }
