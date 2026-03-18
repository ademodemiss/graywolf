# Phase 267 Monitoring Checklist

Phase 267’de senin bakmanı istediğim üç kısa madde:

1. **Learning reliability sinyalleri:**
   - `monitor/replan_learning_reporter.py` veya benzeri script’ten gelen son raporun `learning_reliability_score`, `learning_warning_rate`, `learning_failure_count` alanlarını kontrol et.
   - Eğer reliability score %70’in altına düştüyse, ops kanalında (Telegram/Slack) ek bir uyarı görmüş olmalısın.

2. **Failure/pending eşiklerini izle:**
   - `learning_failure_count` veya `pending` 4-5’in üzerine çıktıysa, aynı rapor sana nedenini (workflow, feedback text, duration) bildiriyor; bunu kontrol edip gerekirse manuel müdahale planla.
   - Bu eşiklerin üzerine çıkmadan önce `monitor/learning_feedback_resolver.py --detail --last` komutunu çalıştır ve `self_improve_learning.log` içindeki son entry’i incele.

3. **Ops+dashboard sinyalleri:**
   - Dashboard’da `learning_reliability`, `learning_warning_rate`, `learning_failure_count` kartlarını şeritleyecek şekilde kontrol et; kartlar `N/A` veya boşsa veri üretimi durmuş demektir.
   - Eğer ek bir notification gerekiyorsa (örneğin eşiğe takılan rapor), `Phase 267 Learning Reporter` cron job’ının logunu `logs/phase266_learning_reporter.log` veya ilgili Telegram mesajlarını kontrol et.

Bu üç maddeyi her gün ya da feedback eşiği tetiklendiğinde hazırla; ciddi bir sapma yoksa Phase 267 hattı stabil demektir. Hazır olduğunda beni “tamam” diye haberdar et, bir sonraki planı (Phase 268) hazırlamaya başlarım.
