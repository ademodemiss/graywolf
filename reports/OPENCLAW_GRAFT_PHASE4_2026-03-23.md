# OPENCLAW_GRAFT_PHASE4_2026-03-23

## 1) Faz
FAZ 4 — Channel experience / Telegram uyumu

## 2) Faz hedefi
Telegram yanıt kontratını OpenClaw benzeri kanal deneyimine yaklaştırmak: kısa ama anlamlı çıktı, next_step görünürlüğü, daha güvenli chunking.

## 3) Yapılan analiz / değişiklik
- `telegram_bot.py`
  - `split_chunks(...)` güçlendirildi:
    - boş metin -> `(çıktı yok)` fallback
    - chunk strip + boş chunk engelleme
  - `_format_result(...)` zenginleştirildi:
    - `mode`, `triage(kind/reason)`, `next_step`, `errors` alanları eklendi
    - fallback çıktısı normalize edildi
- `tests/test_telegram_bot_bridge.py` (new)
  - chunking/placeholder testleri
  - format_result alan görünürlüğü testleri
- `docs/OPENCLAW_SOURCE_MAP.md`
  - `telegram_bot.py` satırı `in-progress` güncellendi

## 4) Dokunulan dosyalar
- `telegram_bot.py`
- `tests/test_telegram_bot_bridge.py` (new)
- `docs/OPENCLAW_SOURCE_MAP.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_telegram_bot_bridge.py tests/test_cli_agent_command.py` -> PASS
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- Telegram tarafında kullanıcıya dönen cevap artık sadece summary değil; `mode/triage/next_step` ile daha aksiyon alınabilir.
- Uzun/boş çıktı davranışı daha güvenli hale geldi.
- Runtime/execution çekirdeğine dokunulmadı.

## 7) Commit hash
- (commit sonrası doldurulacak)

## 8) Kalan iş
- FAZ 5: Tool orchestration uyarlaması

## 9) Sonraki faz
- FAZ 5 — Tool orchestration uyarlaması
