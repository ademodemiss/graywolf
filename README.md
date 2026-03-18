# GrayWolf Projesi

## Amaç
GrayWolf, Ubuntu VPS üzerinde çalışan, tamamen yeni ve bağımsız bir ajan sistemidir. Güvenli, genişleyebilir ve 7/24 arka planda çalışabilen bir altyapı olarak teslim edilecektir.

## Hızlı Navigasyon (Toparlanmış)
- Repo haritası: `docs/REPO_MAP.md`
- Operasyon merkezi: `docs/ops/OPERATIONS.md`
- Toparlama planı: `REPO_CLEANUP_PLAN.md`
- Envanter raporu: `reports/repo_inventory.json`

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

### Faz 101 — Temel Görev Araçlarının Genişletilmesi (Ofis & Veri İşleme)
- `ExcelTool`: Excel dosyaları üzerinde okuma, yazma ve sayfa oluşturma yeteneği.
  Örnek Kullanım:
  ```bash
  python3 tools/excel_tool.py --file my_data.xlsx --action create_sheet --sheet NewSheet
  python3 tools/excel_tool.py --file my_data.xlsx --action write --sheet DataSheet --data '[["Ad", "Soyad"], ["Atlas", "AI"]]'
  python3 tools/excel_tool.py --file my_data.xlsx --action read --sheet DataSheet
  ```
- `MailTool`: E-posta taslakları oluşturma, onaylama ve gönderme yeteneği. SMTP bağlantı testi ve sağlayıcı doğrulama desteği.
  Örnek Kullanım:
  ```bash
  python3 tools/mail_tool.py --action draft --to "recipient@example.com" --subject "Test Mail" --body "Bu bir test e-postasıdır."
  python3 tools/mail_tool.py --action test-smtp
  # draft-id ile onaylama veya gönderme
  ```


### Faz 102 — Finansal Veri Analizi ve Bilgi Sunumu
- `FinancialDataTool`: `yfinance` kütüphanesini kullanarak hisse senedi verilerini (geçmiş fiyatlar, temel bilgiler) çekme yeteneği.
  Örnek Kullanım:
  ```bash
  python3 tools/financial_data_tool.py --action get_stock_data --ticker AAPL --period 1mo
  python3 tools/financial_data_tool.py --action get_ticker_info --ticker MSFT
  ```
- `AnalysisTool`: Çekilen finansal verileri LLM kullanarak analiz etme ve kısa özetler sunma yeteneği.
  Örnek Kullanım:
  ```bash
  # Önce veriyi çek (örneğin financial_data_tool ile), sonra analiz_tool'a JSON olarak ilet.
  # Örnek: python3 tools/analysis_tool.py --ticker AAPL --data "{\"price\": 150, \"volume\": 1000}"
  ```


### Faz 103 — Gelişmiş Kodlama ve Kendi Kendini Geliştirme Yetenekleri
- `CodeTool`: LLM kullanarak belirli gereksinimlere göre kod üretme ve mevcut kodu analiz etme (açıklama, iyileştirme, hata tespiti) yeteneği.
  Örnek Kullanım:
  ```bash
  python3 tools/code_tool.py --action generate_code --requirement "Python'da iki sayıyı toplayan fonksiyon" --language python
  python3 tools/code_tool.py --action analyze_code --code "def multiply(a, b): return a * b" --analysis_type explanation
  ```
- `SelfImproveTool`: GrayWolf'un kendi loglarını ve geçmiş hatalarını analiz ederek performans iyileştirmeleri ve öğrenme önerileri sunma yeteneği.
  Örnek Kullanım:
  ```bash
  python3 tools/self_improve_tool.py --action get_errors_summary --num_errors 3
  python3 tools/self_improve_tool.py --action analyze_logs --log_content "Son hata logları burada..." --context "Performans iyileştirmesi için"
  ```


### Faz 104 — OAuth Entegrasyonu ve Güvenli Yetkilendirme
- `OAuthTool`: Google Drive gibi harici servisler için OAuth 2.0 kimlik doğrulama akışlarını yönetme, token kaydetme ve yenileme yeteneği.
  **Önemli Not:** Bu aracı kullanabilmek için, Google Cloud Console'dan indirilen `credentials.json` dosyasını `~/.graywolf/google_credentials.json` yoluna yerleştirmeniz gerekmektedir.
  Örnek Kullanım:
  ```bash
  python3 tools/oauth_tool.py --action authenticate_google_drive
  # Kimlik doğrulama tamamlandıktan sonra, servisleri get_google_drive_service ile kullanabilirsiniz.
  ```


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

Phase 6, GrayWolf'u tek geliştirici ortamından çıkarıp son kullanıcıya hazır hâle getirmeye odaklanıyor. Gmail veya Outlook gibi sağlayıcılar için SMTP kimlik bilgilerini güvenli şekilde tanımlayıp test etmeli, sonra check → test → send akışını uygulamalısınız.

### 1) Provider Setup Wizard
Yeni `.env` şablonunu elde etmek için `tools/provider_setup_wizard.py` çalıştırın. Örnek:
```bash
env PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m tools.provider_setup_wizard \
  --provider gmail --format env --env-file .env
```
Bu komut maskelemiş şablonu, provider notlarını ve `validate_provider_env` çıktısını üretir. `--format json` çıktısını scriptlerle parse etmek için kullanabilir, `--reveal-secrets` ile placeholderları görebilirsiniz.

### 2) `.env` dosyasını doldur
`.env.example` dosyası provider bazlı bölümler (Gmail, Outlook, OAuth2) ve secret saklama yönergeleri içerir. Kopyalayıp (örneğin `cp .env.example .env`) kendi mail adresinizi, `SMTP_PROVIDER` değerini (`gmail` veya `outlook`) ve `SMTP_PASS/SMTP_OAUTH2_TOKEN` gibi gizli alanları güncelleyin. Secretları versiyon kontrol içine almayın; Vault, OS keyring veya deployment sırasında enjekte edilen ortam değişkenleri kullanın.

### 3) Check & Test & Send akışı
1. `validate-provider` ile provider'a özel doğrulamayı çalıştırın:
   ```bash
   env PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m tools.mail_tool \
     --action validate-provider --provider $SMTP_PROVIDER --env-file .env
   ```
   Bu çıktı `missing`, `invalid_format` ve `warnings` kategorilerini içerir.
2. `check-smtp` ile SMTP konfigürasyonunu gerçek zamanlı olarak sınıflandırın:
   ```bash
   python -m tools/mail_tool --action check-smtp --provider $SMTP_PROVIDER --env-file .env
   ```
   `validation.issues` listesi hem eksik/uyumsuz alanları hem de önerileri verir; eksik alanlar sebebiyle `fallback: dry_run` yapılırsa logların incelenmesi önerilir.
3. `test-smtp` ile bağlantı kurup `HELO`/`EHLO` atın, ardından `send --dry-run=false` ile gerçek mail gönderimini devreye alın.

Bu üç adım `check → test → send` pipeline'ını tamamlar; her adımda `logs/terminal.log` dosyası komut ayrıntılarını tutar.

Geliştirici ortamında `tools/provider_setup_wizard.py --provider gmail --format json` gibi komutlar, `memory/2026-03-16.md` gibi günlük dosyalarında saklanabilecek `missing` / `fallback` uyarıları üretiyor. `tools/mail_tool.py --action check-smtp` çıktısı eksik alanları `missing` listesine koyar ve `fallback: dry_run` önerdiği için `.env` içinde eksik olan SMTP_* değerlerini tamamladıktan sonra tekrar çalıştırarak normal akışı doğrulayın.

### 4) Güvenlik ve rotasyon
- Her reset/rotate sonrasında eski `SMTP_PASS`/`SMTP_OAUTH2_TOKEN` değerlerini iptal edip yeni secret'ı sadece güvenli kanallarda saklayın.
- Secret değerlerini chat/grup/topluluk loglarına yapıştırmayın; yalnızca `.env` (veya Vault) gibi kontrollü alanlarda cacheleyin.
- Yeni kullanıcılar için wizard çıktısındaki `secure_storage` notlarını takip edin.

### 5) Dağıtım öncesi doğrulamalar
- `python -m py_compile tools/provider_setup_wizard.py tools/provider_validation.py` komutuyla yeni modüllerin syntax kontrolünü yapın.
- `tools.provider_setup_wizard.py --provider <...> --format env` komutları `logs/terminal.log` içerisinde kaydedilir; bu loglar komut geçmişini ve policy kararlarını gösterir.

## Installation

To set up GrayWolf locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/graywolf.git
    cd graywolf
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **OpenClaw Integration:**
    Ensure OpenClaw Gateway is running and connected.
