# GrayWolf Projesi

## Amaç
GrayWolf, Ubuntu VPS üzerinde çalışan, tamamen yeni ve bağımsız bir ajan sistemidir. Güvenli, genişleyebilir ve 7/24 arka planda çalışabilen bir altyapı olarak teslim edilecektir.

## Temel Kurallar
- Proje Dizini: `~/graywolf`
- Linux Kullanıcısı: `adem` (sudo kısıtlaması nedeniyle mevcut kullanıcı)
- Config Dizini: `~/.graywolf`
- Servis Adı: `graywolf.service`
- Loglar: `~/graywolf/logs/`

### Güvenlik
- Güvenli komutlar otomatik olarak çalışır.
- Riskli komutlar onay gerektirir.
- Tehlikeli sistem değişiklikleri otomatik olarak yapılmaz.

## Mimari
GrayWolf'un dizin yapısı aşağıdaki gibidir:

```
~/graywolf
├── core/             # Çekirdek bileşenler
├── tools/            # Araç tanımlamaları
├── policies/         # Güvenlik ve çalışma politikaları
├── adapters/llm/     # LLM entegrasyon adaptörleri
├── workflows/        # YAML tabanlı iş akışları
├── memory/           # Ajana özel hafıza dosyaları
├── logs/             # Uygulama logları
├── cli.py            # Komut satırı arayüzü
└── README.md         # Proje açıklaması
```

## Fazlı Geliştirme Planı

### Faz 1 — Çekirdek
- Python sanal ortamı (`venv`) kurulumu.
- `TerminalTool`: Güvenli terminal komutları yürütme yeteneği.
- `FileTool`: Dosya okuma/yazma yeteneği.
- `Policy Engine`: Güvenlik ve onay mekanizmaları.
- `Log Sistemi`: Detaylı loglama altyapısı.
- CLI Komutları: `graywolf shell`, `graywolf run`, `graywolf health`

### Faz 2 — LLM Entegrasyonu
- `LLMAdapter` arayüzü: Tak-çıkar LLM mimarisi.
- En az 1 sağlayıcı (örn. OpenAI, Gemini) için adaptör desteği.
- `Plan → Tool çağır → Sonucu değerlendir` döngüsü.

### Faz 3 — Workflow
- YAML tabanlı workflow runner.
- Örnek workflow: Klasör analizi ve rapor üretme.

### Faz 4 — 7/24 Çalışma
- `systemd` servis dosyası oluşturma.
- Servisi etkinleştirme ve başlatma.
- Servis sağlık kontrolü.

## Kullanıcı Kurulumu (Faz 6)

### 1) Provider şablonu üret
```bash
python3 /home/adem/graywolf/tools/provider_setup_wizard.py --provider gmail --format env
python3 /home/adem/graywolf/tools/provider_setup_wizard.py --provider outlook --format env
```

### 2) `.env` oluştur
```bash
cp /home/adem/graywolf/.env.example /home/adem/graywolf/.env
```

### 3) SMTP ayarlarını doğrula
```bash
python3 /home/adem/graywolf/tools/mail_tool.py --action validate-provider --provider gmail
python3 /home/adem/graywolf/tools/mail_tool.py --action check-smtp
python3 /home/adem/graywolf/tools/mail_tool.py --action test-smtp
```

### 4) Güvenlik notu
- Secret değerleri (API key, SMTP_PASS, token) chat/log içine düz metin olarak yazmayın.
- Key/password değişiminde eski değeri iptal edin (rotate).
