# Message Triage Gate Finalize — 2026-03-22

Durum: FINALIZED
Kapsam: assistant girişinde chat vs task ayrımı yapan minimal triage gate.

## Kısa Finalize Notu
- Assistant girişine dar kapsamlı `chat|task` triage katmanı eklendi.
- Chat kalıplarında agent loop tetiklenmeden sohbet cevabı dönülüyor.
- Task kalıplarında mevcut assistant->agent akışı aynen korunuyor.
- Belirsiz mesajlarda agent run başlatılmadan kısa clarifying yanıt dönülüyor.
- Execution/policy/approval hattına dokunulmadı.

## Doğrulama
- Test: `tests/test_cli_agent_command.py`, `tests/test_simple_agent_loop.py`, `tests/test_cli_agent_continuity.py` PASS (`24 passed`)
- Precheck: PASS
- Acceptance örnekleri:
  - `Merhaba` -> `mode=chat`
  - `Nasılsın` -> `mode=chat`
  - `iki sayıyı toplayan script yaz` -> task path (`mode=plan_only`, triage=`task`)

Not: Bu turda yeni feature/refactor/tuning açılmadı; yalnız triage fix turu stabilize edilip finalize edildi.
