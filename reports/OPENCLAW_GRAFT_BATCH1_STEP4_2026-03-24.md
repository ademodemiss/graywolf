# OPENCLAW_GRAFT_BATCH1_STEP4_2026-03-24

## 1) Faz
Post-migration Batch-1 / Adım-4 — Tool payload visibility parity (non-breaking)

## 2) Faz hedefi
Assistant çıktı sözleşmesinde tool-orchestration kararlarını görünür kılmak; runtime davranışını değiştirmeden kanal/UI tarafında izlenebilir metadata sağlamak.

## 3) Yapılan değişiklik
- `core/graywolf_cli.py`
  - `_build_tool_payload_meta(...)` eklendi.
  - `assistant_output` içine `tool_payload_meta` eklendi.
  - `tool_payload_meta` alanları:
    - `intent`, `triage_kind`, `route`, `tool_family`, `risk`, `session_id`, `source`
  - Chat/plan_only/run yanıtlarında metadata üretiliyor.
- `tests/test_cli_agent_command.py`
  - `assistant_output.tool_payload_meta` doğrulamaları eklendi.

## 4) Dokunulan dosyalar
- `core/graywolf_cli.py`
- `tests/test_cli_agent_command.py`
- `reports/OPENCLAW_GRAFT_BATCH1_STEP4_2026-03-24.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_cli_agent_command.py tests/test_assistant_llm_decision.py tests/test_telegram_bot_bridge.py` -> PASS (22 passed)
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- Tool payload visibility parity non-breaking şekilde tamamlandı.
- Assistant çıktı kontratı kanal/UI tüketimi için daha açıklanabilir hale geldi.
- Runtime/execution çekirdeği etkilenmedi.

## 7) Commit hash
- (commit sonrası)

## 8) Kalan iş
- Batch-1 kapanış: full regression + e2e canonical acceptance + finalize

## 9) Sonraki faz
- Batch-1 Finalize
