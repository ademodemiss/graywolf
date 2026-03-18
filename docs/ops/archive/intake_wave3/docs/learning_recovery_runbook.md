# Learning Recovery Runbook

Bu runbook, Phase 268-270 boyunca öğrenme/log iyileştirme akışını takip ederken hangi komutları, dosyaları ve threshold’ları kullanman gerektiğini anlatır. Her adımda script’lerin çıktısını kontrol et ve sonrasında next step’leri uygulamayı unutma.

## 1. Learning recovery summary & insights
- `monitor/learning_recovery_coordinator.py` ile `logs/learning_recovery_summary.log`’a kısa özetler yazdırdık. Ops olarak bu script’i `--telegram` ile çalıştırırsan aynı log kaydını bir Telegram mesajı olarak da alırsın (bu Phase 269’un ana raporudur).
- `monitor/learning_recovery_inspector.py` (Phase 270 hedefi) summary + learning + suggestions verilerini birleştirerek `logs/learning_recovery_insights.json` dosyasını oluşturur ve aşağıdakileri sana verir:
  - Autopilot retry sayısı + ortalama reliability
  - En çok retry alan workflow’lar ve neden (reliability<%70, failure count≥3, trend alert vs.)
  - `suggested_action` alanı (örneğin: `manual review`, `increase timeout`, `hold queue`) ve `alert_message` (predictive alert içeriği)
  - Komut: `cd /home/adem/graywolf && PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_inspector.py --learning-log logs/self_improve_learning.log --summary-log logs/learning_recovery_summary.log --suggestions logs/learning_recovery_suggestions.json --output logs/learning_recovery_insights.json` (opsiyonel `--telegram` veya `--dry-run`).
  - Cron job: `Phase 270 Learning Recovery Inspector` her 6 saatte bir aynı komutu `--telegram` ile çalıştırır, böylece ops summary’leri otomatik alır ve `learning_recovery_insights.json` sürekli yenilenir.
- Bu dosyanın içeriğini ops dashboard’unda (Phase 270’te kartlar) ve Telegram summary’lerde görüyorsun; `learning_recovery_insights.json` kusurluysa script’leri yeniden çalıştırıp hatayı tekrar test et.

## 2. Trend & autpilot ile manual müdahale
- `monitor/learning_reliability_trends.py` warning rate’te %10 artış ya da 24 saatlik pencere içinde reliability düşüşü tespit ederse Telegram’a `Phase 268 Predictive Alert` gönderir. Alert geldiğinde `logs/learning_recovery_suggestions.json` içindeki `trend` bölümünü oku (# indicator). Eğer `alert_message` yoksa, trend summary’sine göre `suggested_action: izleme` ya da `manual review` notlarını değerlendir.
- `monitor/replan_learning_autopilot.py` reliability<%70 veya failure_count≥3 durumu gördüğünde yeni job tanımlar ve `logs/learning_recovery.log`’a yazar. Bu log, Phase 269 summary’lerinin ve inspector’ın ana girdisidir; autopilot job’ları incelenmeden phase 271’e geçme.

## 3. Manual resolution — `learning_feedback_resolver.py`
- Bir job’u manuel olarak yeniden planlamak ya da neden failure olduğunu öğrenmek istiyorsan:
  1. `monitor/learning_feedback_resolver.py --last --detail` ile en son failure entry’sini al.
  2. Girşin `workflow`, `learning_status`, `learning_feedback`, `learning_follow_up_notes` alanlarını not et.
  3. Ops’tan `Phase 270` değerlendirmesini yaparken, eğer reliability score < 50 ise `SelfImproveTool` ile manuel replan girdisi eklemeyi düşünebilirsin.
  4. Gerekirse `replan` log’unu ( `logs/self_improve_replan.log` ) açarak hangi approval request’in (GRANTED/denied) beklediğini kontrol et.

## 4. Hangi dosyaları nereye bakmalı?
| Komut | Hangi dosya | Ne amaçla | İlgili Phase |
| --- | --- | --- | --- |
| `learning_recovery_coordinator.py` | `logs/learning_recovery_summary.log` | 24 saatlik summary | Phase 269 |
| `learning_recovery_inspector.py` | `logs/learning_recovery_insights.json` | Detaylı insights + öneriler | Phase 270 |
| `learning_reliability_trends.py` | `logs/self_improve_learning.log`, `learning_recovery_suggestions.json` | Predictive alert | Phase 268 |
| `replan_learning_autopilot.py` | `logs/self_improve_replan.log`, `logs/learning_recovery.log` | Otomatik retry | Phase 268 |
| `learning_feedback_resolver.py` | `logs/self_improve_learning.log` | Manual çözüm | Phase 268-270 |

## 5. Ops’a tavsiye
- Cron sonuçlarını incele: `Phase 269 Learning Recovery Coordinator` her 4 saatte bir summary yolluyor. `openclaw cron list` çıkışında bu job görünmeli; en azından son 3 kayıt `logs/learning_recovery_summary.log` içinde yer almalı.
- Eğer trend alert (`alert_message`) gelmiş ama `learning_recovery_insights.json` boşsa, clear cache: `monitor/learning_recovery_coordinator.py --dry-run` sonra `--telegram` komutunu bir daha çalıştır.
- Manuel müdahale gereken job varsa, inspector içinde `suggested_action: manual review` notunu arayarak `monitor/learning_feedback_resolver.py --last --detail`’ı çalıştır.

Bu runbook Phase 270’dan sonra Phase 271’e geçerken referansın olacak; daha fazla detaya ihtiyaç duyarsan runbook’u birlikte genişletiriz.## 6. Phase 271 reliability alarm
- `monitor/learning_recovery_alerts.py --telegram` reliability ortalaması düşükse veya insight severity’leri critical/warning seviyesine çıkıyorsa `logs/learning_recovery_alerts.log`’a entry yazar ve ops’a Telegram mesajı gönderir. Log her seferinde `learning_flag: processed_by_phase266` ve `processed_flag: processed_by_phase271` içerir.
- Cron job `Phase 271 Reliability Alert` günde iki kez çalışır; komut şu:
  ```
  PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python monitor/learning_recovery_alerts.py --telegram
  ```
- Telegram mesajlarındaki `reasons` bölümüne bakarak hangi workflow’lar ya da trend değişimleri alarmı tetiklediğini gör. Ops olarak `learning_recovery_alerts.log`’u takip et, her log satırındaki `insights` başlıklarını not et.
- Alarm `warning` ya da `critical` olduğunda `monitor/learning_feedback_resolver.py` ile hem job geçmişini (`--last --detail`) hem de `learning_recovery_insights.json`’u referans alarak `suggested_action` listesini manuel planlamaya çevir. Ops runbook’unda Phase 271 alt başlığına bu adımları ekledim; `docs/phase271_monitoring.md`’te de aynı hatırlatmalar yer alıyor.

Bu runbook Phase 270’dan sonra Phase 271’e geçerken referansın olacak; daha fazla detaya ihtiyaç duyarsan runbook’u birlikte genişletiriz.

## 7. Phase 272 trend + pending otomasyonu
- `monitor/learning_recovery_trend.py` (varsayılan 12 saatlik pencere) `logs/self_improve_learning.log` içindeki `learning_status`, `learning_feedback`, `learning_event`, `learning_duration_ms`, `learning_reliability_score` ve yeni metadata’ları okuyup `learning_success_rate`, `pending_count`, `reliability`, `warning_count`, `start_sources`, `learning_events` gibi metrikleri hesaplar. Severity `critical` (reliability<%50) veya `warning` (pending>3 ya da reliability<%65) olarak belirlenir, her çalışmada `reasons` ve `trend history` `logs/learning_recovery_trend.log`’a kaydedilir.
- Ops: `--telegram` ile çalıştırıldığında sadece `warning`/`critical` durumlarında Telegram mesajları yollanır; `--dry-run` ile log yazmadan test yapılabilir. Cron `Phase 272 Trend Watcher` her 6 saatte bir bu komutu çıktığında (default pencere + `--telegram`), `learning_recovery_trend.log` dosyasında history birikir ve dashboard’a `learning_recovery.trend` alanını sağlar.
- Dashboard: `dashboard/templates/index.html`’in “Trend Metrikleri” kartı en son entry’den `success_rate`, `pending`, `reliability`, `latest_feedback`, `reasons` özetlerini ve history’yi gösterir. `/api/status` çıktısında `learning_recovery.trend.latest` var mı diye kontrol et; yoksa script’i tekrar çalıştırıp log’u yeniden oluştur.
- Cron testi: `learning_recovery_trend.log`’da son satır yeni bir `ts` taşıyor mu, `trend.latest` alanı JSON olarak geliyor mu, Telegram summary (warning/critical) gelmedi ama log yazıldı mı diye kontrol et. Ops gerekirse manual `PYTHONPATH=/home/adem/graywolf python monitor/learning_recovery_trend.py --dry-run` ile hazırlık yapabilir.

Bu runbook Phase 272 operasyonunda trend ve pending izlemeyi kolaylaştırmak için referansın olacak; gerekirse adımları genişletiriz.
