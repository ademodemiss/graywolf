# HYBRID_TRIAGE_LLM_FINALIZE_2026-03-23

## Scope
- Assistant triage katmanında minimal/hybrid LLM entegrasyonu.
- Execution/policy/approval/queue/worker/runtime akışlarına dokunulmadı.

## Changes
- `core/graywolf_cli.py`
  - `_infer_triage_with_llm(message)` eklendi (strict JSON parse + whitelist kind: `chat|task|unclear`).
  - `_triage_message_kind(message)` rule-based korunup sadece belirsizde LLM fallback/hybrid karar alacak şekilde güncellendi.
  - `cmd_assistant(...)` tarafında `unclear` yolunun chat/clarify UX’e düşmesi netleştirildi (agent loop tetiklenmez).
- `tests/test_assistant_triage_hybrid.py` eklendi.

## Validation
- `python -m pytest -q tests/test_assistant_triage_hybrid.py tests/test_cli_agent_command.py` -> PASS (18 passed)
- `scripts/graywolf precheck` -> PASS

## Safety/No-break
- Conservative escalation: net rule-based chat/task kararları aynen korunur.
- LLM parse fail/timeout/invalid enum/düşük confidence -> mevcut fallback davranışı.
- `unclear` sonucu task path’e sokulmaz.
