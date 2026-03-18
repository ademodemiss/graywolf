# Phase 267 – Learning Feedback & Reliability Loop

## Amaç
Phase 266’da approval → learning job hattını canlı tutup cron’la learning özetlerini ops kanalına gönderdik. Phase 267’nin amacı, bu learning feedback’lerini operasyonel sinyallere çevirip, sistemin kendi çıktılarının güvenilirliğini izlemek ve gerektiğinde insan müdahalesini tetiklemektir.

## Hedefler
1. **Learning feedback analizi:** `logs/self_improve_learning.log` üzerindeki entry’leri periyodik olarak tarayıp "feedback": "success"/"warning"/"failure" kategorilerine ayır. En son öğrenme döngüsünün hangi workflow’tan çıktığını, önerinin ne kadar sürede tamamlandığını ve approval sonrası hangi takip raporunu (errors/warnings) ürettiğini kayıt altına al.
2. **Reliability sinyalleri:** Dashboard’a `learning_reliability_score`, `learning_warning_rate` ve `learning_failure_count` kartları ekle. Bu metrikleri `monitor/replan_learning_reporter.py` veya yeni `monitor/replan_learning_feedback.py` script’inden besle.
3. **Ops eskalasyon:** Eğer success rate 24 saatte %70’in altına düşerse veya pending job sayısı 5’i geçerse ops/e-posta/Telegram’dan ek bir uyarı at. Aynı zamanda bu durumdan Phase 267 kontrol listesi (doküman ve checklist) birkaç dakika içinde seni haberdar eder.
4. **İnsan müdahalesi:** Feedback pipeline’ı, `learning_failure_count` belirli bir eşiğin üzerine çıktığında `monitor/learning_feedback_resolver.py` gibi bir script ile en son job detayını toplayıp sana bir özet rapor ve gerekirse manuel yeniden çalıştırma komutları sunar.

## Kabul kriterleri
* `logs/self_improve_learning.log`’dan alınan entry’ler, artık `learning_feedback_category` (success/warning/failure) ve `learning_reliability_score` alanları içeriyor.
* `monitor/replan_learning_reporter.py` veya yeni script `learning_reliability_score`, `learning_warning_rate`, `learning_failure_count`, `pending` ve `last_feedback` gibi metrikleri hesaplayıp Telegram/ops kanalına raporlayarak durumu özetliyor; ayrıca `learning_failure_count` eşiklerini geçtiğinde ekstra uyarı veriyor.
* Dashboard’taki `learning` paneli yeni kartlarla genişledi, `monitor/dashboard/data.py`’ya yansıyor.
* `docs/phase267_monitoring.md` Phase 267’de seni sadece birkaç adımda takip ettiren bir checklist sunuyor.

## Bir sonraki adım
1. Learning log entry formatını genişlet (feedback_category, reliability_score, follow_up_notes) ve `self_improve_learning.log`’a yaz.
2. `monitor/replan_learning_reporter.py`’i yeni reliability metriklerini hesaplayacak/kritik eşiği kontrol edecek hale getir; eşiğe takıldığında ops kanalına ekstra telegram gönder.
3. Ops channel için Phase 267 Learning Feedback cron job’ı ayarla (günde 2 kez çalışan), ayrıca failure count eşiği çıktığında ayrı bir Telegram mesajı çıkar.
4. `docs/phase267_monitoring.md` ve `NEXT_ACTION.md` Phase 267 checklist’ini içerecek şekilde güncelle, ardından Phase 268 planı için hazır sinyalini bekle.
