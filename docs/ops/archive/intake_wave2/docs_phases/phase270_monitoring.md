# Phase 270 Monitoring Checklist

Phase 270’da artık learning recovery summary’leri ve trend özetlerinden yola çıkarak hangi workflow’ların tekrar çalıştırıldığına, reliability topluluğunun nerede düştüğüne ve ops’un ne yapması gerektiğine bakıyoruz. Aşağıdaki kısa checklist bu içgörüleri doğrulamanı sağlıyor:

1. **Learning recovery inspector’ı çalıştır:**
   - Komut: `cd /home/adem/graywolf && PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_inspector.py --recovery-log logs/learning_recovery.log --summary-log logs/learning_recovery_summary.log --suggestions logs/learning_recovery_suggestions.json --output logs/learning_recovery_insights.json` (opsiyonel: `--dry-run` veya `--telegram`).
   - Çıktıda son 24 saatlik pencere için: kaç autopilot retry gerçekleştiğini, ortalama reliability’yi, `pending`/`failure` trendlerini ve `trend.alert_message` veya `suggested_action` bazlı önerileri gör.
   - Eğer bir workflow üç defa retry borsasında yer alıyorsa tek satırlık notta bu işin `learning_recovery_insights.json` içinde listelendiğini kontrol et.

2. **Learning recovery runbook’u kullan:**
   - `docs/learning_recovery_runbook.md` dosyasındaki adımları takip ederek hangi script’lerin hangi loglarla eşleştiğini, ops’ta manuel müdahale gerekiyorsa ne yapılması gerektiğini, hangi durumlarda `monitor/learning_feedback_resolver.py` komutunun çalışması gerektiğini hatırla.
   - Runbook’ta bahsedilen `learning_recovery_insights.json` parçalarının `recommended_action` ve `alert_message` alanlarını doğrula.

3. **Dashboard kartını gözden geçir:**
   - Yeni `learning_recovery insights` kartı (ya da mevcut `learning_recovery` kartı) `dashboard/templates/index.html`’deki summary’ı ve `learning_recovery_insights` verilerini gösteriyor olmalı; kart, her insight’ı `[severity] title (suggested action)` formatında listeler.
   - `dashboard/server.py --test` çalışmasını `learning_recovery` alanıyla test ettir (yeni `learning_recovery_insights` alanı da dahil). Kartta retry sayısını, avg reliability’yi, son retry sebebini ve önerilen action’ı açıkça gör.

4. **Inspector cron job’u çalışır durumda tut:**
   - Cron ismi: `Phase 270 Learning Recovery Inspector`, komutu `cd /home/adem/graywolf && PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_inspector.py --output logs/learning_recovery_insights.json --telegram`.
   - `openclaw cron list` çıktısında job aktif olmalı, `nextRunAt` 6 saat aralıklarla ilerlemeli ve en az bir son çalışma `logs/learning_recovery_insights.json`’a insight eklemiş olmalı.
   - Cron çalıştıkça Telegram’da insight özetleri düşüyor; `docs/learning_recovery_runbook.md`’deki cron bölümünde açıklanan komutlarla eşleşip, ops’a gereken bağlam veriliyorsa bu kısım tamamlanmış sayılır.
   - `Phase 269 Learning Recovery Coordinator` cron job’u runbook’un bir parçası. `openclaw cron list` ile job’un hala aktif, `nextRunAt` 4 saatten kısa ve Cron’un son çalışması `logs/learning_recovery_summary.log`’da yer alıyor mu diye bak.
   - Inspector script’inin `logs/learning_recovery_insights.json` ve summary log’larındaki timestamp’leri karşılaştırarak veri gecikmesi yoksa, inspektör cron job (yakında planlanacak) için referans ver.

Bu checklist’i tamamladığında Phase 270’ın ops’a sunduğu farkları doğrulamış olursun. Herhangi bir adımda belirsizlik olursa bana ilet, birlikte detaylandırırız. İstersen bu checklist’i Phase 271 planına referans olacak şekilde `docs/phase271_monitoring.md`’e genişletmeye şimdiden başlayabilirim.