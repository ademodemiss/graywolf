# Phase 270 – Learning Recovery Playbook & Reliability Tuning

## Amaç
Phase 269’da learning recovery summary’lerini ops’a düzenli olarak sunduk; Phase 270’ın hedefi bu döngüyü bir "playbook" ve içgörü kartı haline getirip reliability sinyallerini detaylıca yorumlamaya, manuel müdahale ihtiyaçlarını yakalamaya ve threshold’ları ayarlamaya hazır hale gelmek.

## Hedefler
1. **Recovery içgörüleri:** `monitor/learning_recovery_inspector.py` gibi bir script ile `logs/learning_recovery_summary.log`, `logs/learning_recovery_suggestions.json` ve `logs/self_improve_learning.log` içeriğini karşılaştırarak:
   - Son 24 saat içinde hangi workflow’larda tekrar retry oluştuğunu,
   - Reliability score dağılımını (metric: `avg_reliability`, `failure_rate`, `pending`),
   - Trend/alert uyumsuzluklarını (örneğin warning rate artışları) saptayıp,
   - `logs/learning_recovery_insights.json`’a kaydedilecek ek öneri kartları ve `ops/telegram` çıkışı için kısa durum notları üret.
2. **Ops runbook genişletmesi:** `docs/learning_recovery_runbook.md` dokümanı oluşturup Phase 268-269’da yazdığımız adımları (autopilot, trend, summary, manual resolver, inspector cron) tek bir yerde toplamak, operasyona:
   - Hangi komutla `learning_recovery_inspector` ve `learning_recovery_coordinator` çıktılarının eşleştiğini,
   - Hangi durumlarda manuel müdahale gerektiğini (örneğin 3 retries + trend alert) ve nasıl ilerleyeceğini, ve
   - Hangi log dosyalarında neyi okuması gerektiğini anlatmak.
3. **Dashboard bağlantıları:** `dashboard/data.py`/`server.py`/`templates/index.html`’e learning recovery insights kartı ekleyerek:
   - Summary log’tan son pencere özetini gösteriyor (retry sayısı, avg reliability, last retry reason),
   - `learning_recovery_insights.json` içeriğindeki önerileri (``suggested_action`` vs. `alert_message`) kaynağa bağlıyor,
   - Ops’a bir bakışta Phase 270 durumu görünür hale getiriyor.
4. **Plan/devam dokümantasyonu:** `docs/phase270_monitoring.md` ops checklist’ini (inspector + runbook + dashboard + cron) anlatıyor ve `NEXT_ACTION.md` Phase 270 görevlerini listeliyor; Phase 271 için hangi metric’lere ihtiyacımız olduğunu not ediyor.

## Kabul kriterleri
* `monitor/learning_recovery_inspector.py` açıkça tanımlanmış pencere/threshold’ları kullanarak insights üretir, dosyaya yazılan `learning_recovery_insights.json` ile dashboard/runbook’u besler ve ops’a gereken Telegram mesajlarını (non-`--dry-run`) oluşturur.
* `docs/learning_recovery_runbook.md` Phase 268-270’u kapsayan, hangi komutların hangi kronlar/raporlarla ilgili olduğu ve manuel müdahale akışını anlatan tek merkezli kılavuz sunar.
* Dashboard’ta yeni `learning_recovery` kartı Phase 270 insights’ları yansıtır; `dashboard/server.py` testi bu alanları zorlar.
* `docs/phase270_monitoring.md` ve `NEXT_ACTION.md` Phase 270 görevlerini net olarak tarif eder, ops’a neleri kontrol edeceklerini söyler ve Phase 271 için hangi verilerin yeterli olduğuna dair not bırakır.

## Bir sonraki adım
1. `monitor/learning_recovery_inspector.py`’ı tasarlayıp sample verilerle çalıştırarak `learning_recovery_insights.json` çıktısını ve ops’a giden Telegram mesajını doğrula.
2. `docs/learning_recovery_runbook.md` ile ops’a tüm learning recovery komutlarını tek bir rehberde topla; gerekirse bu dokümanı `docs/phase270_monitoring.md`’e referansla bağla.
3. Dashboard kartını ve `dashboard/server.py` testini Phase 270 insights’a göre güncelle.
4. `NEXT_ACTION.md`’i Phase 270 listesiyle yenile, Phase 271 için hangi metric’leri toplamak gerektiğini not et (örneğin `learning_recovery_insights.json` içinde reliability trendleri vs.).
