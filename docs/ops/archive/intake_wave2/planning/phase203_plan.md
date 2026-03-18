# Phase 203 Plan — Gelişmiş Hata Kurtarma ve Dayanıklılık

Bu belge, artık GrayWolf roadmap'inde kalan Faz 203'e (Gelişmiş hata kurtarma ve dayanıklılık) sistematik şekilde yaklaşmak için izlenecek adımların kontrol listesidir. Faz, yüksek hata oranı/maks-tekrar gibi durumları tespit eden, otomatik kurtarma başlatan ve sonuçları raporlayan altyapıyı inşa etmeyi amaçlıyor.

## Ana hedefler
1. **Gözlem & tespit:** İş kuyruğu/çalışan durumlarından metrikler topla ve hata spike'larını belirle (örn. retry oranı, dead-letter sayısı, node kaybı).
2. **Eylem & kurtarma:** Durumu doğruladıktan sonra ilgili node/yeni görevler için restart/retry müşterek işlemlerini tetikle.
3. **Rapor & alarm:** Yeniden başlatma/determinasyon kararlarını loglayıp alert gönder (alert kanalı: logs + Telegram/alert modülleri).
4. **Simülasyon/test:** Yeni davranışları çalıştırabilir şekilde CLI/modül haline getirip, test komutlarıyla doğrula.

## Bölümlere ayırma (chunk strategy)
- `phase203/01-foundation.md`: node_manager ve incident_response altyapısını güçlendiren değişiklikler.
- `phase203/02-detection.md`: metrik toplayıcılara dayalı hata tespiti ve threshold tanımları.
- `phase203/03-recovery.md`: yeniden başlatma/incident yanıtı için koordinatör modülü.
- `phase203/04-validation.md`: test komutları, örnek koşular ve raporlama adımları.

Her alt dosya tamamlandığında kısa bir durum raporu (birkaç satır) yazılacak ve bu plan dosyasındaki ilgili adım ✅ yapılacak.

## İlk adım: Temel altyapıyı hazırlamak
1. `cluster/node_manager`'a `update_node`/`get_node` gibi yardımcılar ekle.
2. `infra/incident_response` içinde durum değerlendirme (node sıralaması, severity) ve restart/mock recovery fonksiyonları yaz.
3. Bu değişikliklerin etkisini `phase203/01-foundation.md` içinde belgeleyip commit benzeri bir özette raporla.

Bu plan çerçevesinde ilerleyeceğim; gerektiğinde iç fazlara tetikleyici ajanlar kurup (örn. `monitor/recovery_coordinator` bir cron/loop modülü gibi çalışabilir) süreci otomatikleştireceğim.

## İlerleme notları
- [x] `cluster/node_manager` modülüne `get_node`, `update_node`, `EventTypes.NODE_UPDATED` desteği eklendi.
- [x] `infra/incident_response` yeniden yazılarak metrik tespitleri, node restart kararları ve logging/alert mekanizmaları tanımlandı.
- [x] `monitor/recovery_coordinator` modülü eklendi: hazır metriklerle veya canlı ölçümlerle kurtarma döngüsü başlatabiliyor.
- [x] `monitor/metrics_collector` logic'i genişletildi; `failure_rate`, `dead_letter_count`, `unhappy_tasks` gibi yeni metrikler hesaplanıyor (bkz. `planning/phase203_detection.md`).
- [x] `monitor/recovery_dispatcher` EventBus üzerinden tetiklenen olaylarda `run_recovery_cycle` çağırıyor ve `logs/recovery_dispatcher.log` da ayrıntılı kayıt tutuyor.
- [x] `tests/test_recovery_cycle.py` yazıldı ve `python3 -m tests.test_recovery_cycle` çalıştırıldı (3/3 OK).
- [x] `tests/test_recovery_dispatcher.py` yazıldı ve `python3 -m tests.test_recovery_dispatcher` çalıştırıldı (2/2 OK).
