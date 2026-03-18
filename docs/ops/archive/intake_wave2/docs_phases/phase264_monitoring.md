# Phase 264 – Replan Feedback İzleme ve Canlıya Alma Dokümanı

Bu doküman, Phase 263’te oluşturulan replan → self-improve → Telegram → ApprovalManager hattını canlıya taşırken ihtiyaç duyulacak gözlem/teyit adımlarını açıkladığı gibi operasyon ekibini yönlendirmek üzere hazırlanmıştır.

## 1. Sistemin durumu ve hedef
* `monitor/replan_self_improve_bridge.py` EventBus’ta `REPLAN_READY` / `REPLAN_EXECUTED` olaylarını dinleyip log analizini Telegram’a yazıyor ve `ApprovalManager` üzerinden `ApprovalRequest` çıkarıyor.
* Uzman onayı (Phase 204 hattı) `monitor/approval_callback_router.py`’ın callback_data’larını `EventTypes.APPROVAL_*` olaylarına çeviren yönlendiricisi ile EventBus’a geri gönderiliyor.
* Phase 264’te hedef, bu hattın canlı ortamda güvenilir çalıştığını gösterecek dokümantasyon, dashboard kartları ve sorumluluk/operation notları oluşturmaktır.

## 2. Dashboard ve izleme
1. `dashboard/templates/index.html`’de yeni “Replan Bridge Durumu” paneli var; burası en son `self_improve_replan.log` entry’sini, `analysis.status` ve `approval_request.status` alanlarını gösteriyor.
2. `dashboard/data.py` artık `replan_bridge` özetini (`latest_event`, `latest_status`, `approval_request`) ve `replan_bridge_entries` listesini API payload’una ekliyor.
3. Bu verileri sorgulayacak sistemler (dashboard web, API, grafik) 15 saniyelik periyodu koruyarak en güncel approval durumunu gösteriyor.
4. Operasyonun ihtiyacı olması halinde bu API endpoint’i (başlangıç `/api/status`) üzerine `replan_bridge` alanı eklenmiş payload çağrılabilir.

## 3. Loglar ve analiz
* `logs/self_improve_replan.log` her event için JSON satırı içeriyor (`event`, `payload`, `analysis`, `approval_request` vs.).
* Analiz başarısı `analysis.status` alanına `ok`/`error` olarak yazılır; dashboard bu alanı gösterir.
* `approval_request` JSON’u `request_id`, `command`, `status`, `created_at` içerir; `status` Phase 204 aprobación states (pending/granted/denied) aldıkça Logu Update olur.
* Onay gecikmesi takibi: `ApprovalManager.evaluate_command`’den dönen `created_at` ile `monitor/approval_callback_router.py` log’undaki callback entry’si arasındaki fark, `approval_health` metriği olarak ilerleyen aşamada `monitor/metrics_collector.py`’a taşınmalıdır.

## 4. Operasyonel prosedür
1. Telegram onayı gelmediğinde (ApprovalManager içinde pending kalmış) `monitor/approval_callback_router.py` log dosyasındaki `request_id`’yi bulup `EventTypes.APPROVAL_*` olaylarını manuel tetikleyip `ApprovalState.GRANTED`/`DENIED` gönderebilirsiniz.
2. `self_improve_replan.log`’da `analysis.status != ok` ise LLM bağlantısına (LLMRouter) tekrar request atılabilir; `tools/self_improve_tool.py`’daki retry logic devreye alınmalı.
3. `monitor/replan_notifier.py` loglarının rafine edilmesi (örn. `hint`, `workflow_name`), sorgular `tools/self_improve_tool.py`’in `summarize_replan_events` fonksiyonu ile daha iyi anlaşılır.
4. Live ortamda `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` ayarlı değilse `monitor/telegram_alert.py` `'TELEGRAM_NOT_CONFIGURED'` logu üretecek; bu log ops’a bildirilmeli.

## 5. Testler ve kanıt
- `.venv/bin/python -m pytest tests/test_self_improve_tool.py tests/test_self_improve_orchestrator.py tests/test_replan_notifier.py tests/test_replan_self_improve_bridge.py` → 11 testi çalıştırarak bridge + approval hattını doğrulayın.
- `PYTHONPATH=. python3 dashboard/server.py --test` → yeni dashboard payload anahtarlarının olduğunu doğrular.
- Gerekirse `monitor/approval_callback_router.py`’ya doğrudan `approval.grant:<id>` JSON’u post ederek EventBus üzerinden `EventTypes.APPROVAL_GRANTED`’ı tetikleyip approval loglarını izleyin.

## 6. Canlıya Alma Notları (Phase 264 hedefleri)
1. Replan hattı devreye girdiğinde `logs/self_improve_replan.log` dosyasının 20 satırı bir script ile güncellensin; bu script reddedilen/kapanan request’leri raporlasın.
2. Dashboard replan kartı, `approval_request.status` değişimlerini yakından izleyerek `denied` durumunda bir alarm (ops notu) üretsin.
3. Phase 265 planı olarak `SelfImproveTool.improve_from_replan` gibi bir adım eklenebilir; bu adım, `approval_request.status == GRANTED` olan analizleri otomatik `self_improve` görevlerine dönüştürür.
4. Operasyon ekibine her hafta Phase 263/264 raporunu (log count, success rate, approval latency) e-posta veya Slack ile gönderin.

## 7. Sonraki adımlar
* Phase 263 canlıya başlandıktan sonra `planning/phase264_plan.md`’de belirtilen görevleri `NEXT_ACTION.md`’e taşıyıp sorumluluğu netleştirin.
* `monitor/approval_callback_router.py`’da log path `logs/approval_callbacks.log`; bu logları da dashboard’a veya ops script’ine bağlayan küçük bir `monitoring/approval_health.py` modülü oluşturulabilir.
* `self_improve_replan.log`’dan `approval_request.metadata.replan.summary` gibi alanları grafiğe çevirerek replanların neden yapıldığını kısaca gösteren bir panel oluşturun.

Hazırsan bu dokümanı bir sonraki sprint planında kullanabiliriz; istersen tüm adımları kısa görevler hâline dönüştürüp `NEXT_ACTION.md` ya da Trello’ye atabilirim.