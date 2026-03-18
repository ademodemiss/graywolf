# Graywolf Repo Cleanup Plan

## Amaç
Repo'yu üretim odaklı, okunabilir ve sürdürülebilir hale getirmek.

## Mevcut Durum (ilk tarama)
- Toplam mantıksal dosya (tracked + untracked): ~554
- En yoğun alanlar: `post_release/`, `ai/`, `core/`, `tests/`, `monitor/`, `tools/`
- Kök dizinde birden fazla durum/plan dosyası var: `CURRENT_STATE.md`, `NEXT_ACTION.md`, `IMMEDIATE_VALIDATION.md`, `ROADMAP.md`, `RELEASE_CHECKLIST.md`
- Faz bazlı dokümanlar dağınık: `docs/`, `planning/`, `reports/`, `tests/phase*`

## Hedef Yapı
- `core/`, `tools/`, `monitor/`, `adapters/`, `dashboard/` => ürün çekirdeği
- `tests/` => testler (phase fixture'ları dahil)
- `docs/` => tek kaynak dokümantasyon
- `archive/` => eski/kanıt/tek-seferlik script'ler

## Uygulama Fazları

### Faz 1 — Envanter ve Etiketleme (güvenli)
- [ ] Tüm dosyaları `runtime`, `test`, `doc`, `legacy`, `artifact` olarak etiketle
- [ ] Runtime kritik dosya listesini çıkar
- [ ] Kırık import/entrypoint taraması yap

### Faz 2 — Düşük riskli toplama
- [ ] Kökteki operasyon dosyalarını `docs/ops/` altına taşı
- [ ] Faz dokümanlarını `docs/phases/` altında birleştir
- [ ] Tek-seferlik rapor/evidence dosyalarını `archive/reports/` altına al

### Faz 3 — Kod yapısı sadeleştirme
- [ ] `monitor/` içindeki tekrarları birleştir
- [ ] `tools/` içinde kullanılmayan/çakışan modülleri ayır
- [ ] `core/` için net entrypoint + orchestrator akışını sabitle

### Faz 4 — Doğrulama
- [ ] Kritik test seti
- [ ] Dashboard `--test`
- [ ] Monitor zinciri smoke test

### Faz 5 — Teslim
- [ ] Değişiklikleri 3 commit'e böl: (structure/docs/runtime)
- [ ] Basit geçiş notu yayınla

## Not
Taşıma/silme işlemlerinde önce `archive/` kullan, geri dönüşü güvenli tut.
