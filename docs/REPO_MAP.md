# Graywolf Repo Map (Canonical)

Bu dosya, repo karmaşasını azaltmak için "nerede ne var" referansıdır.

## 1) Runtime (ürünü çalıştıran)
- `core/` → orkestrasyon, event bus, agent loop
- `tools/` → terminal, mail, provider setup/validation, guard
- `monitor/` → health/recovery/trend raporlayıcıları
- `adapters/llm/` → LLM sağlayıcı adaptörleri
- `dashboard/` → API + UI
- `workflows/`, `workflow_engine/` → workflow tanımları ve çalıştırıcı

## 2) Test
- `tests/` → otomatik testler
- `verification/` → ek doğrulama scriptleri

## 3) Dokümantasyon
- `README.md` → genel ürün tanımı
- `docs/` → phase ve monitoring dokümantasyonu
- `docs/ops/OPERATIONS.md` → günlük operasyon (tek giriş noktası)
- `docs/phases/INDEX.md` → phase durumlarının kanonik listesi

## 4) Planlama / Geçiş
- `planning/` → faz planları (tasarım aşaması)
- `reports/` → rapor/evidence çıktıları

## 5) Arşiv / Legacy (kademeli sadeleştirme)
- `archive/` → kökten taşınan legacy dosyalar (`archive/root_legacy/`)
- `post_release/`, `ai/`, diğer tarihi içerikler

---

## Sadeleştirme Kuralı
1. Runtime kodu `core/tools/monitor/adapters/dashboard` dışına yayılmasın.
2. Yeni phase notları önce `docs/`, sonra gerekirse `planning/`.
3. Tek-seferlik çıktılar `reports/` altında tutulmalı.
4. Kök dizine yeni md dosyası eklemek yerine `docs/ops` veya `docs/phases` kullanılmalı.
