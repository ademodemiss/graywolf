# Phase 272 Monitoring – Trend ve Pending Otomasyonu

Phase 272’de amacımız learning recovery akışına trend/pending kontrolü ekleyip reliability alarm müracaatını desteklemektir. Aşağıdaki bileşenler bu aşamada takip edilen yapı taşlarını toplar.

## 1. Trend Watcher script’i
- Dosya: `monitor/learning_recovery_trend.py`
- 12 saatlik pencere (varsayılan) boyunca `logs/self_improve_learning.log`’ı okuyor, `learning_status`, `learning_feedback`, `learning_reliability_score`, `learning_event`, `learning_duration_ms`, `start_source` gibi alanları topluyor ve `learning_success_rate`, `pending_count`, `reliability`, ortalama süre, warning sayısı gibi metrikleri hesaplıyor.
- Severity: reliability < %50 → `critical`, reliability < %65 veya pending > 3 → `warning`, aksi halde `info`. Gerekçe listesi `reasons` ile kaydediliyor.
- Çıktı: `logs/learning_recovery_trend.log` (günde 4 çalışmada 4 adet yeni satır). Dosya `stats`, `latest_feedback`, `reasons`, `severity`, `start_sources`, `learning_events`, önceki flag’ler ve pencere saati içeriyor.
- Ops: `--telegram` ile çalışırsa, sadece `warning`/`critical` durumlarında Telegram mesajı atıyor; `--dry-run` ile ücretsiz test yapılabilir.

## 2. Dashboard ve ops görünürlüğü
- `dashboard/data.py` artık `learning_recovery.trend` alanını döndürüyor. API (`/api/status`) üzerinden `trend.latest` ve `trend.history` okunarak `dashboard/templates/index.html`’de yeni “Trend Metrikleri” alanı gösterilir (başarı yüzdesi, pending, reliability, son feedback, sebepler, history logları).
- Autopilot/Trend önerileri aynı bölümde kalır; “Reliability Alarm” kartı Phase 271 uyarılarını korur.
- Dashboard’ı `dashboard/server.py --test` ile çalıştırıp `/api/status` çıktısında `learning_recovery.trend.latest`’in ve `trend.history`’in dolu olduğundan emin ol.

## 3. Cron ve doğrulama
- Cron job: `Phase 272 Trend Watcher` (her 6 saatte bir) yürütür: `cd /home/adem/graywolf && PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_trend.py --telegram`.
- Verification: `learning_recovery_trend.log`’ta cron çalışmaları yeni satırlar bırakıyor mu, `nextRunAt` mantıklı mı, ve Telegram’da `warning`/`critical` summary’leri anlık alabiliyor muyuz kontrol et.
- `NEXT_ACTION.md`’de bu cron’un `openclaw cron list`’te aktif olduğunu, `learning_recovery_trend.log`’a satır yazdığını ve dashboard’daki trend kartını güncel tuttuğunu listele.
