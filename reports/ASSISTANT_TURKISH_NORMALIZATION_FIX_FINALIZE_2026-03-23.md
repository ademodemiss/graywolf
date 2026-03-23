# ASSISTANT_TURKISH_NORMALIZATION_FIX_FINALIZE_2026-03-23

## Scope
- Assistant chat-vs-task triage katmanında Türkçe büyük/küçük harf normalizasyonu kaynaklı yanlış sınıflandırma fix'i.
- Execution/policy/approval/queue/worker/runtime akışlarına dokunulmadı.

## Problem
- `SEN KİMSİN` gibi mesajlar bazı Unicode case dönüşümlerinde `uncertain_clarify` yoluna düşebiliyordu.

## Fix
- `core/graywolf_cli.py`
  - `_normalize_for_match(...)` eklendi (casefold + NFKD + combining temizleme).
  - Triage pattern eşleşmeleri normalize metin üstünden çalışacak şekilde güncellendi.
  - Chat UX kontrolü normalize metin üstünden değerlendirildi.

## Validation
- `python -m pytest -q tests/test_cli_agent_command.py tests/test_assistant_triage_hybrid.py` -> PASS (19 passed)
- `scripts/graywolf assistant --message "SEN KİMSİN"` -> `mode=chat`, `triage.reason=chat_pattern`, identity summary doğru.
