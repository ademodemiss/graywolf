# OPENCLAW_GRAFT_PHASE5_2026-03-23

## 1) Faz
FAZ 5 — Tool orchestration uyarlaması

## 2) Faz hedefi
Runtime çekirdeğine dokunmadan, assistant karar çıktısına OpenClaw benzeri orchestration üst-katman sinyali eklemek (route/risk/tool family).

## 3) Yapılan analiz / değişiklik
- `core/graywolf_cli.py`
  - `ASSISTANT_TOOL_ROUTE` matrisi eklendi.
  - `_orchestration_hint(intent)` helper eklendi.
  - assistant `plan_only` ve normal task çıktısına `orchestration_hint` alanı eklendi.
  - Intent normalize mekanizması ile uyumlu çalışacak şekilde bağlandı.
- `tests/test_cli_agent_command.py`
  - assistant plan_only çıktısında `orchestration_hint` doğrulaması eklendi.
  - script isteğinde `chat_command -> safe_execute (low)` doğrulaması eklendi.
- `tests/test_assistant_orchestration_hint.py` (new)
  - route mapping ve invalid intent fallback testleri eklendi.
- `docs/OPENCLAW_SOURCE_MAP.md`
  - orchestration satırı `in-progress` olarak güncellendi.

## 4) Dokunulan dosyalar
- `core/graywolf_cli.py`
- `tests/test_cli_agent_command.py`
- `tests/test_assistant_orchestration_hint.py` (new)
- `docs/OPENCLAW_SOURCE_MAP.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_assistant_orchestration_hint.py tests/test_cli_agent_command.py tests/test_assistant_llm_decision.py` -> PASS
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- FAZ 5 kapsamında tool orchestration üst-katman sinyali assistant çıktısına eklendi.
- Bu sayede channel/UI tarafı karar rotasını daha açık gösterebilir.
- Execution/runtime hattına dokunulmadı.

## 7) Commit hash
- (commit sonrası doldurulacak)

## 8) Kalan iş
- FAZ 6: End-to-end acceptance + stabilizasyon

## 9) Sonraki faz
- FAZ 6 — End-to-end acceptance + stabilizasyon
