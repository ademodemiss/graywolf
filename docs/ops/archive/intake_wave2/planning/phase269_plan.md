# Phase 269 – Learning Recovery Coordination & Ops Runbook

## Amaç
Phase 268 ile reliability sinyallerini ops kanalına ve dashboard’a taşıdık; Phase 269’un hedefi artık bu sinyalleri birer operasyonel özetten geçirerek geçirgenliği, tekrar eden recovery pattern’lerini ve manu̇el müdahale ihtiyaçlarını netleştirmek.

## Hedefler
1. **Learning recovery özetleyici:** `monitor/learning_recovery_coordinator.py` gibi bir script ile `logs/learning_recovery.log` ve `logs/learning_recovery_suggestions.json` içeriğini al, son 24 saatlik pencere için kaç otomatik retry olduğunu, ortalama reliability score’u, son retry nedenini ve dashboard önerilerini çıkar, bunu hem yeni `logs/learning_recovery_summary.log`’a yaz hem de ops’a kısa Telegram mesajı olarak gönder.
2. **Dashboard + ops runbook:** Learning recovery özetini Phase 269 monitoring checklist’ine, ops runbook’una ve `learning_recovery_suggestions.json`’a bağla; böylece otomatik recovery çağrıları ile insan müdahalesi kesi̇şimini hızlıca görebilirsin.
3. **Cron destekli izleme:** Yeni özetleyici scripti cron’a ekleyip belirli aralıklarla (4 saatte bir/6 saatte bir) çalıştır, zonun bir sonraki penceresinde `learning_recovery_summary.log`’a yeni özetler düşsün ve Telegram raporu gelsin.

## Kabul kriterleri
- `monitor/learning_recovery_coordinator.py` özet kaydı yazıyor, ops’a uygun formatta mesaj üretiyor, summary log’u `logs/learning_recovery_summary.log`’a ekliyor; script `--dry-run` ve `--telegram` opsiyonlarını destekliyor.
- `logs/learning_recovery_summary.log` üzerinden geçmiş summary’lar takip edilebiliyor (timestamp, retry sayısı, ortalama reliability, son yeni request).
- Cron işlerinde `Phase 269 Learning Recovery Coordinator` scripti düzenli çalışıyor; ops channel’ına gelen mesajlarda summary ve varsa `learning_recovery_suggestions` içeriği gözüküyor.
- `docs/phase269_monitoring.md` Phase 269 checklist’ini verebiliyor, ops’un neyi hangi komutla kontrol edeceğini söylüyor; `NEXT_ACTION.md` Phase 269 için atılacak adımları gösteriyor.

## Bir sonraki adım
1. `monitor/learning_recovery_coordinator.py`’ı örnek loglarla çalıştırarak çıktıları/summary log’u doğrula. 
2. Cron job’un `Phase 269 Learning Recovery Coordinator` olarak tanımlı olduğundan ve Telegram çıktılarının doğru formatta olduğundan emin ol (saatlik/dört saatte). 
3. `docs/phase269_monitoring.md`’i güncelle, ops checklist’ini Phase 269’a özel hale getir ve gerekli komutları yaz.
4. `NEXT_ACTION.md`’i Phase 269 görevleriyle yeniden düzenle; Phase 270 planını hazırlamak için hangi veri setlerine ihtiyacımız olduğunu not et.
