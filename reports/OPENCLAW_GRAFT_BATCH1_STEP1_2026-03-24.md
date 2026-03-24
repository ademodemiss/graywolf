# OPENCLAW_GRAFT_BATCH1_STEP1_2026-03-24

## 1) Faz
Post-migration Batch-1 / Adım-1 — Assistant output contract parity hardening

## 2) Faz hedefi
Assistant yanıtlarının kanal/tüketici tarafında daha standart tüketilebilmesi için tek bir sözleşme nesnesi üretmek.

## 3) Yapılan değişiklik
- `core/graywolf_cli.py`
  - `_assistant_output_contract(...)` helper eklendi.
  - `cmd_assistant` chat/plan_only/run dönüşlerine `assistant_output` alanı eklendi.
  - `assistant_output` içinde:
    - `contract_version: v1`
    - `mode`
    - `triage {kind, reason}`
    - `response {summary, next_step}`
    - `orchestration`
- `tests/test_cli_agent_command.py`
  - chat + plan_only senaryolarına `assistant_output` doğrulamaları eklendi.

## 4) Dokunulan dosyalar
- `core/graywolf_cli.py`
- `tests/test_cli_agent_command.py`
- `reports/OPENCLAW_GRAFT_BATCH1_STEP1_2026-03-24.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_cli_agent_command.py tests/test_telegram_bot_bridge.py tests/test_assistant_llm_decision.py` -> PASS (21 passed)
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- Assistant çıktı sözleşmesi v1 aktif.
- Mevcut runtime/execution hattı etkilenmeden channel-parity için daha deterministik response yapısı sağlandı.

## 7) Commit hash
- (commit sonrası)

## 8) Kalan iş
- Batch-1 / Adım-2: LLM decision schema parity derinleştirme (traceability alanları).

## 9) Sonraki faz
- Batch-1 / Adım-2
