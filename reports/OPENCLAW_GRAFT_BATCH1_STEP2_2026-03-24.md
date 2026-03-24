# OPENCLAW_GRAFT_BATCH1_STEP2_2026-03-24

## 1) Faz
Post-migration Batch-1 / Adım-2 — LLM decision schema parity + traceability

## 2) Faz hedefi
LLM karar katmanında daha açıklanabilir karar üretmek: LLM denendi mi, parse oldu mu, kullanıldı mı, fallback nedeni ne sorularını cevaplayan iz alanları eklemek.

## 3) Yapılan değişiklik
- `core/graywolf_cli.py`
  - `_infer_goal_with_llm` çıktısına `trace` alanı eklendi:
    - `llm_attempted`
    - `llm_parsed`
    - `llm_used`
    - `fallback_reason`
  - LLM kapalı/parse fail/non-string/exception durumlarında fallback nedeni net atanıyor.
  - LLM actionable değilse (`llm_not_actionable`) izlenebilir şekilde kaydediliyor.
- `tests/test_assistant_llm_decision.py`
  - trace alanları için doğrulama testleri eklendi/güncellendi.

## 4) Dokunulan dosyalar
- `core/graywolf_cli.py`
- `tests/test_assistant_llm_decision.py`
- `reports/OPENCLAW_GRAFT_BATCH1_STEP2_2026-03-24.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_assistant_llm_decision.py tests/test_cli_agent_command.py` -> PASS (17 passed)
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- LLM decision katmanı artık daha izlenebilir ve operasyonel olarak debug edilebilir.
- Runtime çekirdeğine dokunulmadı.

## 7) Commit hash
- (commit sonrası)

## 8) Kalan iş
- Batch-1 / Adım-3: Telegram outbound parity (sanitize/contract detay eşleme).

## 9) Sonraki faz
- Batch-1 / Adım-3
