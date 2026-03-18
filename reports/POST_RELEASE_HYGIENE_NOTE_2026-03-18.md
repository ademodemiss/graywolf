# Post-Release Hygiene Note — 2026-03-18

## Durum
- Release baseline tamam ve main green.
- Working tree'de lokal modified/untracked gürültü var.

## Bugün yapılan güvenli deneme
- Gürültüyü stash ile izole etmeye çalışıldı.
- `precheck` bazı untracked içeriklere bağımlı olduğundan ilk denemede fail görüldü.
- Stash geri açma sırasında untracked overlap çakışması oluştu (dosyalar zaten mevcut).

## Karar
- Veri kaybı riski oluşturmamak için otomatik hard-clean uygulanmadı.
- Çalışma ağacı mevcut haliyle korundu.
- Operasyonel doğrulama tekrar yapıldı: `scripts/graywolf precheck` PASS.

## Önerilen güvenli sonraki adım
- Hijyen turunu ayrı bir maintenance branch'te, yol bazlı whitelist ile (keep/archive/drop) ve adım adım restore planı ile yürüt.
