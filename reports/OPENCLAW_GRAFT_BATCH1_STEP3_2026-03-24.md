# OPENCLAW_GRAFT_BATCH1_STEP3_2026-03-24

## 1) Faz
Post-migration Batch-1 / Adım-3 — Telegram outbound parity hardening

## 2) Faz hedefi
Telegram kanalına giden assistant çıktılarının daha güvenli ve tutarlı görünmesi için sanitize + contract uyumunu sıkılaştırmak.

## 3) Yapılan değişiklik
- `telegram_bot.py`
  - `_sanitize_for_telegram(...)` eklendi:
    - CRLF normalizasyonu
    - görünümü bozabilecek kontrol karakterlerinin temizlenmesi
    - trim
  - `_format_result(...)` dönüşü sanitize pipeline'dan geçirildi.
- `tests/test_telegram_bot_bridge.py`
  - sanitize kontrol karakter temizliği testi eklendi.

## 4) Dokunulan dosyalar
- `telegram_bot.py`
- `tests/test_telegram_bot_bridge.py`
- `reports/OPENCLAW_GRAFT_BATCH1_STEP3_2026-03-24.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_telegram_bot_bridge.py tests/test_cli_agent_command.py` -> PASS (18 passed)
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- Telegram outbound cevap kalitesi/paritesi güçlendi.
- Control-char kaynaklı bozulmaların önüne geçildi.
- Runtime çekirdeğine dokunulmadı.

## 7) Commit hash
- (commit sonrası)

## 8) Kalan iş
- Batch-1 / Adım-4: tool payload visibility parity (non-breaking metadata yüzeyi).

## 9) Sonraki faz
- Batch-1 / Adım-4
