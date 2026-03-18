# Learning Feedback Guide

Bu kılavuz, Phase 268 otonom müdahaleleri takiben bir problem çıktığında hangi adımları izlemen gerektiğini anlatıyor.

1. **Son failure/warning entry’sini incele:**
   - `monitor/learning_feedback_resolver.py --last --detail` ile `self_improve_learning.log`’daki en son failure veya warning kaydını getir.
   - Bu çıktı sana workflow, status, feedback ve follow-up notlarını sağlar; hangi workflow’un neden düşük reliability verdiğini hızlıca gör.

2. **Autopilot yeniden denemelerini kontrol et:**
   - `logs/learning_recovery.log`’da otomatik denemeler kaydediliyor. Ekibin sisteme müdahale etmeden önce hangi request_id’lerin tekrar çalıştığını buradan görebilirsin.
   - Eğer `scheduler` sonuçları `logs/learning_recovery.log`’da `processed` alanını içeriyorsa, bu job artık queue’ya eklendi.

3. **Trend uyarılarını, öneri kartlarını ve ops mesajlarını değerlendir:**
   - `monitor/learning_reliability_trends.py` sürekli warning rate delta’sını takip eder. `Phase 268 Predictive Alert` Telegram mesajları gönderildiyse, `logs/learning_recovery_suggestions.json` dosyasında hem trend hem autopilot özetlerini bulursun.
   - Dashboard’daki `learning_recovery` kartları sana hem autopilot özetini hem de trend önerisini yazar; burada `retry / manual review` gibi notlar görebilirsin.

4. **İnsan müdahalesi gerektiğinde:**
   - Autopilot başarısız olursa, `monitor/learning_feedback_resolver.py --last --detail` çıktısındaki workflow ve feedback bilgisiyle o job’u manuel olarak yeniden planlayabilirsin.
   - İhtiyacın olursa `monitor/learning_feedback_resolver.py --count 3` gibi komutlarla önceki birkaç failure’ı da inceleyebilirsin.
   - Gerekiyorsa `SelfImproveTool`’ı doğrudan çalıştırmadan önce kontrol edilen job’u `logs/self_improve_replan.log`’a manuel ekleyebilir veya approvals tarafında tekrar GRANTED isteği tetikleyebilirsin.

Her müdahale sonunda `logs/learning_recovery.log`’a yeni kayıtlar ekleniyor; ops ekibiyle birlikte bu log’u izleyerek sistemin nasıl tepki verdiğini belgeleyebilirsin.
