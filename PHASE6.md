# Phase 6 — Multi-Provider User Setup (Productization)

## Amaç
GrayWolf'u tek geliştirici ortamından çıkarıp son kullanıcı kurulumuna uygun hale getirmek.
Her kullanıcı kendi mail sağlayıcısını (Gmail/Outlook) güvenli biçimde bağlayabilmeli.

## Milestone 1 — Provider Setup Wizard (CLI)
- `tools/provider_setup_wizard.py` oluştur
- Sağlayıcı seçimi: `gmail | outlook`
- Çıktı: provider'a göre `.env` için gerekli alanları üret
- Secret alanlarını maskele (`***`) ve doğrulama uyarıları ver

## Milestone 2 — Config Validation Layer
- Ortam değişkenlerini provider'a göre doğrula
- Eksik/zayıf değerleri kategorize et (`missing`, `invalid_format`, `warning`)
- `mail_tool.py --action check-smtp` ile uyumlu rapor üret

## Milestone 3 — Secure Storage Guidance
- `.env.example` provider bazlı şablon
- Secret saklama yönergesi: plaintext paylaşma yasağı, rotate adımı
- Kurulum sonrası test akışı: check -> test -> send

## Milestone 4 — UX + Release Integration
- `README.md`'ye "Kullanıcı Kurulumu" bölümü ekle
- `RELEASE_CHECKLIST.md` Faz 6 maddeleri ekle
- Kanıt: py_compile + wizard dry-run + terminal.log

## Başarı Kriteri
- Yeni kullanıcı 5-10 dk içinde provider kurulumunu tamamlayabilmeli
- Gmail ve Outlook için ayrı net alanlar + test adımları sunulmalı
- Varsayılan olarak geliştirici hesabına bağımlılık kalmamalı
