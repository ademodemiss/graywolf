# Phase 271 Monitoring – Reliability Alerts & Ops Readiness

Phase 271, learning recovery insights kartını reliability alarmına dönüştürmeyi hedefliyor. Bu doküman, gözlemler, cron job’ları ve dashboard metrilerini takip etmen için gereken adımları toparlar.

## 1. Reliability alarm script’i
- `monitor/learning_recovery_alerts.py` günde iki kez çalışarak `logs/learning_recovery_insights.json`’u okur, reliability ortalaması, pending sayısı ve insight severity’lerini değerlendirir.
- `--telegram` argümanıyla sadece `warning` ya da `critical` seviyesinde uyarılar gönderen Telegram mesajı atar.
- Her çalışmada `logs/learning_recovery_alerts.log`’a JSON satırı eklenir; içinde severity, gerekçeler, insight başlıkları ve learning flag’leri olur.

## 2. Cron job’ları
- `Phase 271 Reliability Alert` cron job’u: `cd /home/adem/graywolf && PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_alerts.py --telegram`
  - Günde iki kez (yaklaşık 12 saat aralıklarla) çalışacak şekilde planlandı.
  - `openclaw cron list` çıktısında aktif olmalı ve `nextRunAt` 12 saat aralıkları göstermeli.
  - Cron çıktıları (gelecek .log satırları) ops’a reliability alarmı olarak telegram’dan bildirilecek.

## 3. Dashboard & ops kontrolü
- `dashboard/templates/index.html`’de Learning Recovery bölümünün altında `Reliability Alarm` kartını kontrol et.
  - `alert-summary` ve `alert-history` alanlarında en son severity’ler görünmeli.
  - Dashboard’ı `dashboard/server.py --test` ile çalıştırıp `/api/status` çıktısında `learning_recovery.alerts` alanının geleceğini doğrula.
- `docs/learning_recovery_runbook.md`’de Phase 271 handoff bölümünü okur ve `monitor/learning_feedback_resolver.py` gibi manual çözüm adımlarını hatırla.

## 4. Doğrulama & next step
- Cron job’un en az bir `warning` veya `critical` uyarı üretmesi durumunda `learning_recovery_alerts.log` dosyasını inceleyip sebebe bak.
- Ops için `monitor/learning_feedback_resolver.py`’ı kullanarak hatalı workflow’ları analiz et ve runbook’ta gerekli karar noktalarını güncelle.
- Phase 272’ye geçmeden önce reliability alarmın trips’ini ve manual adımları ops ekibiyle paylaş.

## 5. Operasyonel teyit (beklemede)
- Manuel `monitor/learning_recovery_alerts.py --telegram` çalıştırması tamamlandı; log ve Telegram çıktısı var ancak doğal cron henüz tetiklenmedi.
- Cron job’undaki bir sonraki çalışmayı bekleyip log + Telegram çıkışını doğrulamak ops checklist’inde ayrı bir onay maddesi olarak kalacak.
- Bu doğal tetik behavı onaylanmadan Phase 271’i kapatmıyoruz; bir sonraki çıkış tamamlandığında kayıtlara “tamam” diyeceğiz ve Phase 272’ye geçeceğiz.
