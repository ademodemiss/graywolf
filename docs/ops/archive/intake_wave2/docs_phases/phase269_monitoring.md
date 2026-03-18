# Phase 269 Monitoring Checklist

Phase 269’da ops’un elinde artık hem reliability sinyalleri hem de otomatik retry özetleri var. Bu checklist her şeyi gözden geçirmene yardım eder:

1. **Learning recovery summary script’i çalıştır:**
   - Komut: `cd /home/adem/graywolf && PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_coordinator.py --recovery-log logs/learning_recovery.log --suggestions logs/learning_recovery_suggestions.json` (istediğinde `--telegram` ekleyebilirsin).
   - Çıktıda kaç retry yapıldığı, son waiting reason, trend özetleri ve ortalama reliability olacak. Hatalıysa loglara (logs/learning_recovery_summary.log) baktığında kayıtların güncel olup olmadığını kontrol et.
   - `--dry-run` ile sadece çıktı alıp dosya yazmayı atlayabilirsin; kalıcı kayıt istiyorsan `--summary-log logs/learning_recovery_summary.log` kullanarak son entry’yi dinle.

2. **Summary log’u doğrula:**
   - `logs/learning_recovery_summary.log` içine her çalıştırmada şu alanlar giriyor: `ts`, `window_hours`, `autopilot_retries`, `avg_reliability`, `last_retry`, `anti_pattern` (trend alert mesajı). Son entry’yi `tail -n 5` ile kontrol et.
   - Yeni özet, `learning_recovery_suggestions.json` içindeki autopilot/trend summary’leri referans alıyor; `learning_recovery_summary.log`’da 24 saatlik pencere içinde (autopilot retry sayısı 0 değilse) bu değerleri doğrula.

3. **Cron job’u izle:**
   - Cron ismi: `Phase 269 Learning Recovery Coordinator`, her 4 saatte bir (`anchorMs=1773316800000`, `everyMs=21600000`). `openclaw cron list` çıktısında aktif, `nextRunAt` güncel olmalı.
   - Cron job’un `stdout` ve `logs/learning_recovery_summary.log` kayıtlarını karşılaştır; Telegram’a summary kaydı düştüyse bu script “Phase 269” rutinini besliyor demektir.

4. **Ops runbook & dashboard bağlantısı:**
   - `learning_recovery_suggestions.json` dosyasındaki `autopilot` ve `trend` özetlerinin dashboard’da göründüğünden emin ol (Phase 268’de açtığın kartlar halen geçerli). Bu script her çalıştırmada o verileri de okur.
   - Operasyon raporunu Telegram’a `monitor/learning_recovery_coordinator.py --telegram` ile attıysan, `Phase 269 learning recovery summary` notları `ops` kanalına düşüyor; manuel müdahale gerekiyorsa `monitor/learning_feedback_resolver.py`’yi çalıştırarak son entry’yi oku.

Bu maddeleri tamamladıktan sonra “Phase 269 coffee check” diyebilirsin; Phase 270 planı için summary log’lar ve trend alert’leri kullanacağız. Yardımcı olmamı istediğin başka bir şey olursa söyle.
