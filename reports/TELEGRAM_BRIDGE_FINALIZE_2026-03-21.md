# Minimal Telegram Bridge Finalize — 2026-03-21

Durum: FINALIZED
Kapsam: Telegram üzerinden mevcut `graywolf assistant` komutunu tetikleyen minimal bridge.

## Acceptance Özeti
- `telegram_bot.py` eklendi.
- Telegram mesajı `scripts/graywolf assistant --message "..."` akışına bağlandı.
- Komutlar çalışıyor: `/run`, `/plan`, `/status`, `/approvals`, `/approve`.
- Uzun çıktı Telegram limitine göre parçalanıyor.
- Hata durumunda kısa mesaj dönülüyor; bot crash olmadan devam ediyor.
- Konfig: `TELEGRAM_BOT_TOKEN` env var.

## Doğrulama
- Test: `tests/test_cli_agent_command.py`, `tests/test_simple_agent_loop.py`, `tests/test_cli_agent_continuity.py` PASS (`19 passed`)
- Precheck: PASS

Not: Bu turda yeni feature/refactor açılmadı; yalnız bridge parçası stabilize edilip finalize edildi.
