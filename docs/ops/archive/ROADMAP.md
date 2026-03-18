# ROADMAP.md
# GrayWolf Project Roadmap

Bu dosya, projenin fazlara ayrılmış geliştirme yol haritasını ve tamamlanan/yapılacak işleri detaylandırmaktadır.

## Tamamlanan Fazlar (Analiz Edildi/Temel Kurulumlar)
- ✅ **Faz 1:** Çekirdek Bileşenler (Temel araçlar, politika, loglama)
- ✅ **Faz 2:** LLM Entegrasyonu (Temel yapı ve analiz)
- ✅ **Faz 3:** Workflow (Analiz edildi)
- ✅ **Faz 4:** Dokümantasyon ve Proje Durum Dosyaları (Analiz edildi, roadmap güncellendi)
- ✅ **Faz 5:** Testler, Doğrulama ve Güvenlik (Temel testler çalıştırıldı, güvenlik taraması yapıldı, `vulnerable_code.py` temizlendi)

## Tamamlanan Fazlar

### ✅ **Faz 261:** Gerçek LLM Entegrasyonu ve Maliyet Takibi
- ✅ LLM Sağlayıcı Ayarları ve Yapılandırması (API anahtarları, adaptörler)
- ✅ Gerçek LLM Entegrasyonu ve Routing (Maliyet takibi dahil)
- ✅ Orchestrator ve Agent Loop Entegrasyonu
- ✅ Testler ve Dokümantasyon

### ✅ **Faz 101:** Temel Görev Araçlarının Genişletilmesi (Ofis & Veri İşleme)
- ✅ Excel İşlemleri Aracı
- ✅ Mail ve Evrak İşleri Aracı
- ✅ Testler ve Dokümantasyon

### ✅ **Faz 102:** Finansal Veri Analizi ve Bilgi Sunumu
- ✅ Finansal Veri API Entegrasyonu
- ✅ Finansal Veri Analizi Modülü (LLM ile)
- ✅ Testler ve Dokümantasyon

### ✅ **Faz 103:** Gelişmiş Kodlama ve Kendi Kendini Geliştirme Yetenekleri
- ✅ LLM Tabanlı Kod Üretimi ve Analizi
- ✅ Terminal ve Komut Otomasyonu
- ✅ Kendi Kendini İyileştirme Mekanizması (İleri seviye)
- ✅ Testler ve Dokümantasyon

### ✅ **Faz 104:** OAuth Entegrasyonu ve Güvenli Yetkilendirme
- ✅ Hedef Servislerin Belirlenmesi (Google Drive, Outlook vb.)
- ✅ OAuth Akışlarının Uygulanması
- ✅ Güvenli Token Yönetimi
- ✅ Testler ve Dokümantasyon

## Gelecek Faaliyetler (Planlanan İleri Seviye Fazlar)

### ✅ Faz 201: Entegrasyon ve Uçtan Uca Test Senaryoları
- ✅ Entegre test senaryoları belirleme (Örn: Finansal veri çek->LLM analiz->Excel'e yaz)
- ✅ `pytest` kullanarak uçtan uca test betikleri oluşturma
- ✅ Mocklama stratejilerini geliştirme (API, dış servisler için)
- ✅ Test otomasyonunu entegre etme (CI/CD veya düzenli çalışma)
- ✅ Test sonuçlarını raporlama ve izleme

### ✅ Faz 202: Kendi Kendini İyileştirme Döngüsü Otomasyonu
- ✅ `SelfImproveTool` için düzenli log analizi görevleri tanımlama
- ✅ LLM'den gelen önerileri yorumlama ve uygulanabilir görevlere dönüştürme mekanizması
- ✅ GrayWolf'un kendi yapılandırmasını veya kodunu LLM önerilerine göre güncelleme (onay ile)
- ✅ Öğrenme döngüsünün etkinliğini izleme ve değerlendirme

### 🟡 Faz 203: Gelişmiş Hata Kurtarma ve Dayanıklılık
- [x] Görevlerin otomatik yeniden deneme mekanizması (backoff stratejileri ile) — `jobqueue` retry + `monitor/recovery_dispatcher` tetik (plan/rapor `planning/phase203_plan.md`).
- [x] Başarısız görev durumlarını algılama ve düzeltme mantığı — `monitor.metrics_collector` yeni metrikler + `infra/incident_response` karar/detaylı logging.
- [x] Süreç izleme ve aksaklık durumlarında otomatik kurtarma (örneğin servis yeniden başlatma) — `cluster/node_manager` restart update + dispatcher tetiklemeleri ile `run_recovery_cycle` çalışıyor.
- [x] Hata raporlama ve uyarı sistemleri — `logs/recovery_dispatcher.log`, incident logları ve testlerle raporlama hatları teyit edildi.

### 🟡 Faz 204: İnsan Onay Mekanizması
- [ ] Kritik komutlar ve eylemler için manuel onay akışı tanımlama
- [ ] Onay isteklerini sana bildirme mekanizması (örneğin Telegram/e-posta ile)
- [ ] Onay/red yanıtlarını işleme ve ajanın davranışını buna göre ayarlama
- [ ] Güvenlik politikaları ile entegrasyon

### 🟡 Faz 205: Genel Performans Optimizasyonu ve Kaynak Kullanımı
- [ ] LLM çağrılarının token ve zaman maliyetlerini detaylı analiz etme
- [ ] LLM prompt'larını ve yanıtlarını daha verimli hale getirme stratejileri (özetleme, damıtma)
- [ ] Uzun süren veya kaynak yoğun işlemler için asenkron veya arka plan görevleri kullanma
- [ ] Sistem kaynak (CPU, bellek) kullanımını izleme ve optimizasyon

## Güvenlik Notları
- Hassas değerler (`.env`, ortam değişkenleri) güvenli bir şekilde yönetilmelidir.
- API anahtarları ve parolalar asla doğrudan koda veya loglara yazılmamalıdır.
- Kodu temiz tutmak ve gereksiz hassas bilgileri kaldırmak sürekli bir önceliktir.

## Agent-First Faz Planı (Phase A‑E)
Bu kısımda agent-first hattını A’dan E’ye kadar net fazlara ayırdım; yanlış önceki tanımları kaldırarak her fazın odak noktalarını açıklıyorum.

### ✅ Faz A – Repo Audit & Command Intake (implemented; Phase F validation pending)
- Audit: mevcut klasör envanterinin ve agent/tools bileşenlerinin doğruluğunu kontrol eden analysis script’leri (special git checks, inventory raporları).
- Komut katmanı: kullanıcı isteğini kısa plan ve tool listesi çıktısına çeviren JSON planlayıcı.
- LLM adaptörü bu katmana bağlanarak prompt → plan dönüşümünün otomatikleşmesini sağlar.

### ✅ Faz B – Agent Orchestration + Tools (implemented; Phase F validation pending)
- Task decomposer: Faz A planını adım adım tool çağrılarına böler ve queue’ya salar.
- Tool dispatcher: terminal_tool, file_tool, code_tool, excel_tool, mail_tool, report_tool gibi araçları güvenli modda çalıştırır.
- Hata ve yeniden deneme yönetimi: core/task_runner_v2 ve task_recovery bileşenleri desteğiyle retry/onay mekanizması.

### ✅ Faz C – Güvenlik & Onay (implemented; Phase F validation pending)
- policies/shell_policy ve tools/tool_guard entegre edilerek riskli komutlar için human_gate üzerinden kullanıcı onayı alınır.
- Onay bekleyen durumlar memory context’e “pending onay” olarak kaydedilir ve agent kararlarını etkiler.

### ✅ Faz D – Memory / Context (implemented; Phase F validation pending)
- memory/lesson_manager, memory_store ve benzeri bileşenler ile uzun görev bağlamları saklanır.
- Kullanıcı tercihleri, proje durumu gibi state bilgileri “context” olarak tutulur; agent önceki kararları ve onay geçmişini hatırlar.

### ✅ Faz E – Monitoring (Destekleyici Katman)
- monitor/ altındaki Phase 265‑272 script’leri ve telegram/alert hatları, agent-first akışı desteklemek için reliability/trend/insights verisi sağlar.
- Monitoring cronları agent çalışırken arka planda reliability/backstop olarak çalışır; ana senaryo agent-first hattıdır.

### 🔜 Faz F – Gerçek Görev Doğrulaması (planlanan)
- Phase F, doğal dil → plan → tool seçimi → execution → human approval → memory → sonuç raporu zincirinin gerçek görevlerde validasyonu olacak.
- İlk tur için üç hedef belirledim: (1) Basit bir HTML sitesi üretmek ve klasöre koymak, (2) Agent modüllerini `.venv` içinde derleyip kod çıktısı üretmek, (3) Excel tarzı satış tablosu oluşturup CSV olarak kaydetmek.
- Bu görevlerde dispatcher’ın terminal/file/code/excel araçlarını doğru sırayla kullanması, `HumanGate/ApprovalManager`/`ToolGuard` kararlarının kaydedilmesi ve `memory` ile trend/alert loglarına özetler girilmesi gerekiyor.
- Görevler tamamlanıp log/summary çıktıları elde edildikten sonra Phase F resmi olarak “validated” durumuna geçecek.