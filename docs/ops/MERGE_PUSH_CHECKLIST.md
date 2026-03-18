# Merge / Push Checklist (Graywolf)

## A) Teknik doğrulama
- [ ] `scripts/release_precheck.sh` PASS
- [ ] `pytest -q tests/test_v2_runtime_foundation.py` PASS
- [ ] `core.runtime status` çıktısı sağlıklı

## B) Çalışma ağacı
- [ ] `git status` ile istenmeyen dosyalar temiz
- [ ] Sadece hedef kapsam dosyaları stage edildi

## C) Commit hijyeni
- [ ] Commit mesajı kapsamı doğru anlatıyor
- [ ] Doküman + kod + test birlikte güncel

## D) Push öncesi
- [ ] Doğru branch üzerinde misin?
- [ ] Remote doğru mu? (`origin`)

## E) Push sonrası
- [ ] CI `release-precheck` workflow sonucu PASS
- [ ] Gerekirse kısa devir özeti paylaşıldı
