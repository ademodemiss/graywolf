# Agent Recovery + Replanning Finalize — 2026-03-20

Durum: FINALIZED
Kapsam: minimal single-agent loop için recovery + tek adımlık replanning.

## Kabul Özeti
- Failure classification aktif: `timeout`, `failed`, `blocked`.
- Retry sonrası adım tamamen durmak yerine kontrollü recovery deniyor.
- Güvenli durumda adım skip edilerek loop devam ediyor.
- Riskli durumda tek fallback adımı eklenerek minimal replanning uygulanıyor (max 1).
- Trace alanları açık: `recovery_attempt`, `fallback_used`, `replanned`, `failure_classification`.

## Doğrulama
- Test: `tests/test_simple_agent_loop.py` + `tests/test_cli_agent_command.py` PASS
- Precheck: PASS

Not: Bu turda yeni feature/refactor yapılmadı.
