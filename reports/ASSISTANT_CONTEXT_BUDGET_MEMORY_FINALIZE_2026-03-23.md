# ASSISTANT_CONTEXT_BUDGET_MEMORY_FINALIZE_2026-03-23

## Scope
- Assistant katmanında kontrollü context budget + summarized memory assembly.
- Execution/policy/approval/queue/worker/runtime akışlarına dokunulmadı.

## Finalized
1. **100k hard context clamp aktif**
   - `core/assistant_context.py` içinde `DEFAULT_MAX_CONTEXT_TOKENS = 100_000`.
   - Env ile değer gelse bile üst sınır 100k’i aşmıyor.
2. **short-term + summarized long-term memory assembly aktif**
   - short-term: session state + pending approvals + recent runs.
   - long-term: `memory/assistant_memory_summary.json` içinden ilgili özet seçimi.
3. **long-memory yoksa sessiz fallback var**
   - Dosya yok/bozuk durumda long-term boş geçiliyor; akış kırılmıyor.
4. **retrieval şu an overlap tabanlı**
   - Mesaj-token overlap ile ilgili memory summary seçiliyor (minimal v1).

## Validation
- `python -m pytest -q tests/test_assistant_context.py tests/test_assistant_triage_hybrid.py tests/test_cli_agent_command.py` -> PASS (23 passed)
- `scripts/graywolf precheck` -> PASS

## Changed files
- `core/assistant_context.py` (new)
- `core/graywolf_cli.py`
- `tests/test_assistant_context.py` (new)
- `tests/test_assistant_triage_hybrid.py`
