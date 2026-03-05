# Phase 4 (Taslak) — Reliability + Operability

## Amaç
GrayWolf’u üretim-benzeri kullanım için daha güvenilir ve izlenebilir hale getirmek.

## Milestone 1 — Config Profiles
- `.env.example` oluştur (SMTP/Gemini/Codex gerekli değişkenler)
- `tools/mail_tool.py` ve orchestrator için config fallback düzeni
- Kanıt: py_compile + TerminalTool test + terminal.log

## Milestone 2 — Test Harness
- `tests/` altında smoke testler (runner, policy, mail draft/send dry-run)
- tek komutla test: `python3 -m tests.smoke`
- Kanıt: test çıktısı + terminal.log

## Milestone 3 — Observability
- `logs/` için özetleyici script (`tools/report_tool.py`)
- son N logdan hata/timeout/deny metriği çıkar
- Kanıt: örnek rapor çıktısı + terminal.log

## Milestone 4 — Release Checklist
- `RELEASE_CHECKLIST.md` ve `CHANGELOG.md` başlangıcı
- Faz 1-4 kapanış kriterleri ve rollback adımları
- Kanıt: dosya + py_compile (varsa) + terminal.log
