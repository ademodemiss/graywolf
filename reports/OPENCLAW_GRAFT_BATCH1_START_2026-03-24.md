# OPENCLAW_GRAFT_BATCH1_START_2026-03-24

## 1) Faz
Post-migration graft execution — Batch 1 başlangıcı

## 2) Faz hedefi
Upstream OpenClaw kodu içinden gerçekten kullanılacak katmanları Graywolf dosya hedefleriyle eşlemek ve ilk güvenli adaptasyon sırasını kesinleştirmek.

## 3) Yapılan analiz / değişiklik
- `upstream/openclaw` kaynak ağacı tarandı.
- Assistant/chat, LLM, channel outbound, tool orchestration için source-anchor seti çıkarıldı.
- Graywolf target dosyalarla birebir eşleme oluşturuldu.
- `reference-only` (gateway/extensions/apps runtime) alanları net ayrıldı.

## 4) Dokunulan dosyalar
- `docs/OPENCLAW_GRAFT_EXECUTION_MAP.md` (new)
- `reports/OPENCLAW_GRAFT_BATCH1_START_2026-03-24.md` (new)

## 5) Test/precheck
- Kod değişikliği yok; bu tur sadece graft execution mapping.

## 6) Sonuç
- Batch-1 teknik kapsamı ve uygulanma sırası netleşti.
- Bir sonraki turda doğrudan Batch-1/adım-1 kod uyarlamasına geçilecek.

## 7) Commit hash
- (commit sonrası)

## 8) Kalan iş
- Batch-1 Adım 1: assistant output contract parity hardening.

## 9) Sonraki faz
- Batch-1 Adım 1 uygulaması
