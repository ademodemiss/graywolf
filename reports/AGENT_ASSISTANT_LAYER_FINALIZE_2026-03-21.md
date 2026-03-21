# Agent Minimal Assistant Layer Finalize — 2026-03-21

Durum: FINALIZED
Kapsam: doğal dil mesajını goal'a çevirip mevcut single-agent loop ile çalıştıran minimal assistant komutu.

## Kabul Özeti
- `graywolf assistant` komutu eklendi.
- Doğal dilden intent+goal çıkarımı eklendi (güvenli parser + mümkünse LLM iyileştirme).
- Mevcut agent loop tetikleniyor; execution hattına dokunulmadı.
- Kullanıcı çıktısında plan/ilerleme/sonuç görünürlüğü sağlandı (`plan`, `progress`, `final`, `ux`).

## Doğrulama
- Test: `tests/test_cli_agent_command.py`, `tests/test_simple_agent_loop.py`, `tests/test_cli_agent_continuity.py` PASS (`19 passed`)
- Precheck: PASS

Not: Bu turda yeni feature/refactor açılmadı; yalnız bu parça stabilize edilip finalize edildi.
