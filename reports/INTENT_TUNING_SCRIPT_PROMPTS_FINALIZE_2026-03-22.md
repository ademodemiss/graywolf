# Parser/Assistant Intent-Tuning Finalize — 2026-03-22

Durum: FINALIZED
Kapsam: düşük risk script yazma istekleri için dar intent eşleme düzeltmesi.

## Kısa Finalize Notu
- Kök neden: `analyze` intent policy'de tanımsız olduğu için gereksiz `confirm_required` üretiyordu.
- Dar tuning: low-risk script prompt kalıpları (high-risk guard yoksa) `chat_command` intent'ine map edildi.
- High-risk guard kalıpları korunarak bu tuning kapsam dışı bırakıldı.

## Doğrulama
- Test: `tests/test_cli_agent_command.py`, `tests/test_simple_agent_loop.py`, `tests/test_cli_agent_continuity.py` PASS (`21 passed`)
- Precheck: PASS
- Acceptance kanıtı: `assistant --message "iki sayıyı toplayan script yaz" --plan-only` çıktısında `intent=chat_command`.

Not: Bu turda yeni feature/refactor/tuning açılmadı; yalnız bu dar intent fix stabilize edilip finalize edildi.
