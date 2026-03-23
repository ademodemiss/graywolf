# OPENCLAW_GRAFT_PHASE3_2026-03-23

## 1) Faz
FAZ 3 — LLM integration ve decision layer iyileştirmesi

## 2) Faz hedefi
Assistant karar katmanında LLM kullanımını daha güvenli ve deterministik hale getirmek: JSON parse/intent normalize/fallback disiplinini sıkılaştırmak.

## 3) Yapılan analiz / değişiklik
- `core/graywolf_cli.py`
  - `VALID_ASSISTANT_INTENTS` whitelist eklendi.
  - LLM JSON parse için ortak yardımcı: `_extract_json_dict(...)` eklendi (codefence dahil).
  - Intent normalize helper: `_normalize_intent(...)` eklendi.
  - `_infer_goal_with_llm(...)` iyileştirildi:
    - `GW_ASSISTANT_LLM=0` ile LLM goal-intent inference kapanabiliyor.
    - LLM intent whitelist dışındaysa heuristic intent korunuyor.
    - Confidence clamp ve conservative adoption uygulandı.
  - `_infer_triage_with_llm(...)` parse katmanı ortak helper’a alındı; confidence clamp eklendi.
- `tests/test_assistant_llm_decision.py` (new)
  - invalid intent fallback testi
  - codefence JSON parse testi
  - env ile LLM disable testi
  - invalid triage JSON fallback testi
- `docs/OPENCLAW_SOURCE_MAP.md`
  - LLM satırı `in-progress` olarak güncellendi.

## 4) Dokunulan dosyalar
- `core/graywolf_cli.py`
- `tests/test_assistant_llm_decision.py` (new)
- `docs/OPENCLAW_SOURCE_MAP.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_assistant_llm_decision.py tests/test_cli_agent_command.py tests/test_assistant_triage_hybrid.py` -> PASS (25 passed)
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- FAZ 3 kapsamında decision layer daha sağlam hale getirildi.
- LLM kaynaklı bozuk/uygunsuz çıktılar artık daha güvenli şekilde heuristic fallback ile absorbe ediliyor.
- Runtime/execution hattına dokunulmadı.

## 7) Commit hash
- (commit sonrası doldurulacak)

## 8) Kalan iş
- FAZ 4: Channel experience / Telegram parity iyileştirmesi

## 9) Sonraki faz
- FAZ 4 — Channel experience / Telegram uyumu
