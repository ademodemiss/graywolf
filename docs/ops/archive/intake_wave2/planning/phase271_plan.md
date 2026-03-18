# Phase 271 – Reliability Escalations & Ops Readiness

## Amaç
Phase 270’da learning recovery insights kartlarını, cron’ları ve runbook’u çalışır hale getirdik. Phase 271’in hedefi bu içgörüleri güvenlik alarmına ve operasyona bağlamak: güvenilirlik düşüşlerini tespit eden escalatron’lar yazmak, manuel müdahale rehberini ve dashboard’ı genişletmek, ops’la kesin sınırlar paylaşmak ve beklenmedik retleri otomatik tekrar kuyruğuna göndermeyi güvenceye almak.

## Hedefler
1. **Reliability alarm** – `learning_recovery_insights.json` içindeki trend, pending ve retry metriklerinden yola çıkarak reliability düşükse veya trend warning rate artıyorsa ops’a anlık telegram alarmı gönderen ve aynı zamanda loglanan script(ler) oluşturmak.
2. **Manual intervention playbook** – `monitor/learning_feedback_resolver.py` ya da benzeri bir araçla `Logs/self_improve_learning.log` girdilerini analiz eden bir akış ekleyerek hangi durumlarda manuel onay/veri gerektiğini runbook’a yazmak ve ops’ın hangi adımları izleyeceğini netleştirmek.
3. **Dashboard + roadmap visibility** – Phase 271’e özel `docs/phase271_monitoring.md` ve dashboard kartı (mesela reliability threshold göstergesi ile insights trend grafiği) ile hangi metriklerin ops tarafında izleneceğini netleştirmek.
4. **High-confidence escalation cron** – Phase 271 cron job’ları (günde 2) ile reliability/threshold uyarılarını 2 aşamalı olarak Telegram’a atmak, gerektiğinde replan/alert loglarına not bırakmak.

## Teslimatlar
- `monitor/learning_recovery_alerts.py` (veya uzantısı) reliability, warning rate ve pending limitleri baz alıp `logs/learning_recovery_alerts.log`’a entry yazıp Telegram’da iki aşamalı mesaj attıran veri hattı.
- `docs/phase271_monitoring.md` ve güncellenmiş `docs/learning_recovery_runbook.md` ile ops adımları, threshold’lar ve hangi script’lerin çalıştırılacağı açık bir şekilde belgelenecek.
- Dashboard’ta reliability alarmı/kartı ve ops’a özel trend (örneğin son 6 saatlik ortalama reliability) kartı, `dashboard/data.py`/template’leri aracılığıyla gösterilecek.
- Phase 271 cron job’ları tanımlanacak (örn. `Phase 271 Reliability Alert` günde 2) ve `NEXT_ACTION.md` listesinde sorgulanarak `openclaw cron list`’ten takip edilecek.

## Görevler
1. `monitor/learning_recovery_inspector.py` çıktısını okuyup `reliability_score`, `warning_rate_delta`, `pending_count` ve `last_feedback` alanlarını değerlendiren yeni yükseklik/treshold hesaplayan modülün prototipini oluştur.
2. Bu modülle `monitor/learning_feedback_resolver.py`’ı entegre ederek problemli workflow’ları (çoklu retry + trend alert) otomatik etiketle ve ops runbook’ta hangi loglara bakacaklarını anlat.
3. Yeni script’e/cron’a reliability alarm eklerek Telegram’a kısa özet (renkli severity, önerilen action) yazdır; log’a `LEARNING_FLAG` ve `PROCESSED_FLAG` gibi işaretleri koyarak analiz hatalarını takip et.
4. Dashboard veri akışında reliability trend veri yapısını `learning_recovery` alanına ekle, `templates/index.html`’e görünür bir alarm kartı ve trend grafiği ekle, `docs/phase271_monitoring.md`’e dalkonuzu (kimin ne zaman kontrol edeceğini) not et.
5. Phase 271 cron job’larını `openclaw cron add` ile tanımla (günde 2, minimal 3-4 saat aralıklı) ve `NEXT_ACTION.md`’e bu cron’ların doğrulama maddesini ekle.

## Kabul Kriterleri
- Yeni reliability alarm script’i `logs/learning_recovery_alerts.log`’a uyarı yazar, Telegram’a summary atar ve `logs/learning_recovery_insights.json`’u referans alarak hangi workflow/feedback hatasını tetiklediğini açıklar.
- Ops runbook’u Phase 271’e özel karar noktalarını (manual_resolution, requeue suggestions) içerir ve `docs/phase271_monitoring.md` bunları izlemeyi anlatır.
- Dashboard’ta `learning_recovery` bölümü reliability trend/alert kartları içerir, `dashboard/server.py --test` bu alanları döndürür.
- `NEXT_ACTION.md` Phase 271 cron’ları ve testleri listeler; `openclaw cron list` çıktısında bu job’lar aktif görünür.

## Bir sonraki adım
1. Bu planın görev listesinden en kritik 2 işi seç (örn. reliability alarm script’i + cron) ve prototipini yaz.
2. Ops runbook’unda yeni decision point’leri açıklayarak Phase 271’e geçiş için bir çağrı oluştur.
3. Dashboard & monitoring checklist’ini Phase 271 metriklerine göre güncelle.
