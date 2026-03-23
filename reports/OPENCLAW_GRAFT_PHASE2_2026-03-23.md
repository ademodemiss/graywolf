# OPENCLAW_GRAFT_PHASE2_2026-03-23

## 1) Faz
FAZ 2 — Assistant/chat katmanının controlled graft uyarlaması

## 2) Faz hedefi
Graywolf assistant chat girişini OpenClaw benzeri sohbet davranışına yaklaştırmak: soru mesajları gereksiz `uncertain_clarify` yoluna düşmesin, chat contract daha tutarlı olsun.

## 3) Yapılan analiz / değişiklik
- `core/graywolf_cli.py`
  - Triage katmanına `chat_question` kuralı eklendi.
  - Soru kalıpları (`?`, `nedir`, `nasil`, `kim`, `kac`, `hangi`) task kalıbı yoksa chat olarak ele alınıyor.
  - Chat UX'te `chat_question` için ayrı özet/next_step yanıtı eklendi.
- `tests/test_cli_agent_command.py`
  - `Python list nedir?` senaryosu için `chat_question` testi eklendi.
- `docs/OPENCLAW_SOURCE_MAP.md`
  - Assistant/context satırları `in-progress` olarak güncellendi.

## 4) Dokunulan dosyalar
- `core/graywolf_cli.py`
- `tests/test_cli_agent_command.py`
- `docs/OPENCLAW_SOURCE_MAP.md`

## 5) Test/precheck
- `python -m pytest -q tests/test_cli_agent_command.py tests/test_assistant_triage_hybrid.py` -> PASS (21 passed)
- `scripts/graywolf precheck` -> PASS

## 6) Sonuç
- FAZ 2 kapsamında assistant/chat giriş kalitesi bir adım daha iyileştirildi.
- Genel bilgi/soru cümleleri artık daha güvenli şekilde chat yolunda tutuluyor.
- Runtime/execution hattına dokunulmadı.

## 7) Commit hash
- (commit sonrası doldurulacak)

## 8) Kalan iş
- FAZ 3: LLM integration + decision layer parity derinleştirme

## 9) Sonraki faz
- FAZ 3 — LLM integration ve decision layer iyileştirmesi
