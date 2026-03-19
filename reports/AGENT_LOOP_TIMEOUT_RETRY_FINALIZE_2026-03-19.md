# Agent Loop Timeout/Retry Finalize — 2026-03-19

Durum: FINALIZED
Kapsam: yalnız timeout/retry karar katmanı stabilizasyonu.

## İçerik
- Timeout durumda retry (default 1) eklendi.
- Retry sonrası tamamlanmazsa loop `error` ve açık neden ile durur.
- Her adım için kısa summary + attempts alanı üretimi eklendi.
- Loop final sonucu netleşti: `tamamlandı` / `yarım kaldı` + `reason`.

## Acceptance
- Düşük risk görev: gerçek çalıştırmada timeout-retry sonrası yarım kaldı (beklenen karar davranışı çalıştı).
- Onay gerektiren görev: `confirm_required` ile yarım kaldı (beklenen).
- Başarısız görev: testte stop-on-error doğrulandı.
- Boş goal: `empty_goal` hatası doğrulandı.

## Doğrulama
- Test: `tests/test_simple_agent_loop.py` + `tests/test_cli_agent_command.py` geçti.
- Precheck: PASS.

Not: Bu turda yeni feature/refactor yapılmadı.
