# Phase 268 Monitoring Checklist

Phase 268’de yapman gerekenler şöyle:

1. **Autopilot yeniden denemeleri:**
   - `monitor/replan_learning_autopilot.py` (veya benzeri script) çalıştı mı? Son raporda reliability score < %70 veya failure count ≥ 3 olduğu için yeniden deneme yapılmış mı?
   - Eğer yeniden deneme tetiklenmişse, `logs/learning_recovery.log`’da ilgili `request_id` ve action reason kaydı var mı?

2. **Predictive alertler & dashboard:**
   - `learning_recovery_suggestions` kartı dashboard’da görünüyor mu? Kart üzerinde,“retry”/“manual review” gibi notlar yer alıyor mu?
   - `monitor/learning_reliability_trends.py` tarafından gönderilen Phase 268 Predictive Alert Telegram mesajları, warning rate yükseldiğinde ops kanalına düşüyor mu?

3. **İnsan müdahalesi rehberi:**
   - `monitor/learning_feedback_resolver.py`’yi çalıştırarak son failure/ warning entry’si detaylarını ve `learning_recovery_suggestions`taki yönlendirmeyi kontrol et.
   - `monitor/learning_feedback_guide.md` (veya dokümanın) güncel durumda; ops kanalındaki manuel müdahale süreci net bir şekilde anlatılıyor mu?

Bu maddeleri düzenli kontrol ettikten sonra “tamam” de; Phase 269 planını çıkarıp sıradaki hedefleri başlatırım. Yardımcı olmamı istediğin başka bir şey olursa haber ver.
