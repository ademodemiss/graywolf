# Maintenance Sweep — 2026-03-19

Durum: FINALIZED
Kapsam: düşük riskli bakım, feature kapsamı açılmadan.

## Bu turda finalize edilen commit
- `2a28458` — `chore(maintenance): ignore local data xlsx exports to keep workspace clean`

## Uygulanan bakım
- `.gitignore` içine `data/*.xlsx` eklendi.
- Amaç: lokal export dosyalarının yanlışlıkla versiyonlanmasını önlemek.

## Doğrulama
- Local gate: `scripts/graywolf precheck` PASS
- CI release-precheck: main/task green (bu finalize turunda yeniden doğrulanacak)

## Bilinçli ertelenen
- Node20 deprecation uyarısı için ek değişiklik bu turda yapılmadı (kapsam dışı bırakıldı).
