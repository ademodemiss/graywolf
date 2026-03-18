# Phase 266 – Öğrenme Döngüsünü Genişletme ve Gözlem

## Amaç
Phase 265’te Approval = GRANTED replan analizlerini otomatik self-improve joblarına dönüştürdük. Phase 266’nın amacı bu otomasyonun *sonraki öğrenme yöntemlerini* ve *operasyonel görünürlüğünü* genişleterek, tüm sistemi devamlı öğrenen ve kendi davranışını anlayan bir hale taşımaktır.

## Hedeflenen bileşenler
1. **Öneri öğrenme logları:** `monitor/replan_self_improve_scheduler.py` ve `SelfImproveTool` çıktıları artık iyileştirme girişinin hangi data’dan başladığını, job’un sonucunu ve approval sonrası gerçek dünyadaki geri bildirimi (`success`, `follow-up stderr`, vs.) loglayarak “ne öğrendik” sorusunu yanıtlamalı.
2. **Durum kartları ve kontrol listeleri:** `docs/phase266_monitoring.md` altına yeni kartlar eklenip `NEXT_ACTION.md` Phase 266 maddeleriyle güncellenmeli; böylece sen sadece "bu 3 maddeye bak" diyerek operasyonu kontrol edebileceksin.
3. **Öğrenme raporlayıcı:** Yeni bir script (`monitor/replan_learning_reporter.py`) veya `monitor/replan_health_reporter.py`’nin genişletilmesiyle, approval sonrası önerilerin başarı oranı, tamamlanan/pending job sayısı ve learning feedback’leri ops/Telegram’a düzenli olarak bildiren bir çıktı üretilmeli.
4. **Ops sinyalleri:** Dashboard/grafana kartları `learning_success_rate`, `pending_replans`, `last_learning_feedback` gibi metrikleri göstermeli; ayrıca `monitor/approval_health.py` benzeri bir modül `phase266_learning_summary` komutu ile anlık durumu raporlamalı.

## Kabul kriterleri
* `monitor/replan_self_improve_scheduler.py` ve ilgili loglar, her job için `learning_feedback`, `start_source`, `completed_at`, `status` gibi alanları içeriyor; kayıtlar `logs/self_improve_replan.log` veya yeni `logs/self_improve_learning.log` dosyasına ekleniyor.
* `monitor/replan_learning_reporter.py` (veya genişletilmiş `replan_health_reporter`) tüm önerileri işler; Telegram / ops kanalına `learning success rate %X, pending Y` gibi özet sunuyor ve günlük/haftalık raporları `docs/phase266_monitoring.md`’de dışa vuruyor.
* Dashboard tarafında `Phase 266 – Learning` kartları eklenmiş; `dashboard/data.py` ve ilgili template’ler `learning_success_rate` ve `learning_pending` değerlerini besliyor.
* `docs/phase266_monitoring.md` ve `NEXT_ACTION.md` Phase 266 kontrollerini dediğim gibi sade şekilde çıkarıyor; günlük bakış listesi 3 maddeden oluşuyor.

## Örnek akış
1. Cron `monitor/replan_learning_reporter.py` çalışır: `logs/self_improve_replan.log` (veya yeni log) içindeki son 24 saatteki job’ları tarar, her birini `success`/`failure`'a göre sınıflandırır, `learning_feedback` alanını analiz eder.
2. Report çıktısı: `learning_success_rate: %87`, `pending: 3`, `last_feedback: "approval.grant -> job completed with small diff"`. Cron aynı raporu ops Telegram kanalına gönderir; ops takımı “kurulum iyi” der.
3. Dashboard API’si `learning_success_rate` ve `pending` sayısını yeni panelde gösterir; `monitor/approval_health.py` benzeri `monitor/replan_learning_summary.py` script’i bir komutla (örn. `python monitor/replan_learning_summary.py --summary`) çalıştırıp durumu terminalde gösterir.

## Bir sonraki adım
1. `monitor/replan_self_improve_scheduler.py`’yi log genişletmesiyle güncelle (learning feedback + duration + status fields). Yeni veriler `logs/self_improve_replan.log` veya `logs/self_improve_learning.log`’a yazılsın.
2. `monitor/replan_learning_reporter.py` veya benzer bir cron script’i oluştur; periyodik olarak `learning_success_rate`, `pending_count`, `last_feedback` raporu üretsin ve ops/Telegram’a atsın.
3. `docs/phase266_monitoring.md`’ı oluşturup Phase 266 kontrol listesini yaz (bakılacak maddeleri 3-4 satırla özetle). `NEXT_ACTION.md`’a “Phase 266 monitoring checklist” maddesini ekle.
4. Dashboard + `monitor/replan_learning_summary.py` ile bu learning metriklerini göster; panel (veya terminal) seviyesinde “learning success rate”/“pending”/“last job durumu” ver.
5. `memory/2026-03-12.md` (veya uygun tarih) güncellemesi ve sonraki `CURRENT_STATE.md`’de Phase 266 iskeletini özetle.

Hazırsan ilk işi (scheduler loglarını öğrenmeye göre güncelleme) yapmaya başlayayım; istersen sana sadece sonuç özetini koyayım.