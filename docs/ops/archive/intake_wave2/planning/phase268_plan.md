# Phase 268 – Autonomous Recovery & Predictive Signals

## Amaç
Phase 265-267 boyunca approval→learning hattını işledik, reliability metriklerini hesapladık, ops kanalına raporlamalar ve uyarılar koyduk. Phase 268’in amacı artık bu reliability sinyallerini otomatik müdahale döngüsüne taşımak: düşük reliability gördüğünde sistem kendi kendine iyileşme önerilerinde bulunsun, kritik job’ları yeniden başlatsın ve insan onayı gerektiğinde açık, kurallı bir pathway sunsun.

## Hedefler
1. **Otonom yeniden çalıştırma:** `monitor/replan_learning_autopilot.py` veya benzeri bir script tasarla; reliability score %70’in altına veya failure_count arka arkaya 3’e çıktığında en son job’ı otomatik olarak yeniden sıraya koymak için `SelfImproveTool`’ı tetiklesin. Yeniden başlatma kararını `logs/self_improve_learning.log`’a ve ops kanalına kısa bir özetle gönder.
2. **Predictive alerting:** Reliability zaman serisini `monitor/learning_reliability_trends.py` ile topla, `learning_warning_rate` eğilimleri %10 artarsa ops’u `Phase 268 Predictive Alert` Telegram mesajıyla bilgilendir. Ayrıca `dashboard/data.py`’a yeni `learning_recovery_suggestions` kartı ekleyip verileri buradan besle.
3. **Humans-in-the-loop:** `monitor/learning_feedback_resolver.py` ile elde edilen failure entry’lerini ops kanalında manuel olarak çözmek için `monitor/learning_feedback_guide.md` gibi bir doküman yaz; otomatik müdahale sonrası da insanın kaydı tutulsun (`logs/learning_recovery.log`).
4. **Dokümantasyon ve kontrol:** `docs/phase268_monitoring.md` kısa checklist’inde ops’u sadece “autopilot rapor var mı”, “predictive alert draft çıktı mı”, “dashboard kartları güncel mi” ile kontrol ettir.

## Kabul Kriterleri
* `monitor/replan_learning_autopilot.py` reliability/failure eşiklerinde en son job’ı yeniden schedule edip ops kanalına durum özetini atıyor, gerekirse `SelfImproveTool`’ı tetikliyor.
* Yeni trend script’i reliability/warning eğilimlerini hesaplayıp dashboard/data’daki yeni kartları besliyor; telemetry `learning_recovery_suggestions` içinde “yeniden dene”, “manuel müdahale” gibi notlar barındırıyor.
* `monitor/learning_feedback_resolver.py` çıkışı, hatalarda hangi workflow’un neden başarısız olduğunu hemen gösteriyor ve ops’un müdahale kayıtları `logs/learning_recovery.log` içine giriyor.
* `docs/phase268_monitoring.md` Phase 268’i üç kısa maddede kontrol listesi hâline getiriyor ve ops’tan “kontrol ettim” onayı alabilirsin.

## Bir sonraki adım
1. `monitor/replan_learning_autopilot.py`’ı tasarlayıp reliability eşiklerine göre job’ları yeniden sıraya koyan, log + ops çıktısı veren bir workflow yaz.
2. `monitor/learning_reliability_trends.py` + `dashboard/data.py` entegrasyonuyla yeni kartları oluştur, `learning_recovery_suggestions` verilerini dashboard’a taşı.
3. `logs/learning_recovery.log`’u ekle; otomatik veya manuel müdahalelerde ilgili job ID’si ve action reason kayda geçsin.
4. `docs/phase268_monitoring.md` ve `NEXT_ACTION.md`’i güncelle, ops’u kısa kontrol listesiyle hazır hale getir.
5. Phase 269 planı için yeni hedefleri hazırla.
