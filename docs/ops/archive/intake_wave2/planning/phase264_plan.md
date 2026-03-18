# Phase 264 – Replan Feedback ve İzleme / Canlıya Geçiş Desteği

## Amaç
Phase 263’te kurulan replan → self-improve → Telegram → ApprovalManager hattını canlıya taşıdıktan sonra bu geri bildirim döngüsünü izlenebilir hale getirmek, onay durumlarını açıkça göstermek ve replan analizinden çıkan kararları Phase 264’te otomasyona ya da operasyona yeniden bağlayacak bir plan kurmak.

## Hedeflenen Bileşenler
1. **Replan Bridge Sağlık Kartı (Dashboard):** `dashboard/data.py`’da `replan_bridge` kartını genişleterek en son 5 `self_improve_replan.log` satırını, her entry’deki `approval_request.status` ve `analysis.status` değerlerini sunacak, ayrıca log dosyasının temiz ve okunabilir kaldığını kontrol edecek bir gözlem widget’ı hazırlamak.
2. **Operasyonel Kontrol Listesi & Dokümantasyon:** `docs/phase263_replan.md`’e canlı ortamda işleyen Telegram callback’leri, `approval_request` takip yöntemleri, log ağaçları ve approved/denied senaryolarında yapılacaklar için kısa bir kontrol listesi/flow diagram (Markdown tabloları veya maddeler) eklemek.
3. **Phase 264 Yol Haritası:** Bu plan dosyasında yüzeylenen izleme/dokümantasyon çalışmalarının yanı sıra şu adımları netleştirmek:
   - Replan logları `self_improve` aracılığıyla sürekli analiz edilecek (günlük, haftalık pipeline). Her log için EventBus’ta `replan` kategorisiyle `SelfImproveTool.analyze_logs_for_improvements` çalıştırılmalı ve `approval_request` statüsüne göre `SelfImproveTool` önerileri otomatik puanlanmalı.
   - Telegram onay gecikmelerinin (izin verilen `approval_request` ile callback arasında geçen süre) `metrics` metriğinde takip edilmesi gerekir; bunun için EventBus (EventTypes.APPROVAL_*) üzerinden `timestamp` bilgisi taşıtılmalı.
   - Operasyon ekibinin `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` ve `approval_request` ID’lerini takip edecek kısayolları (örn. `monitor/approval_callback_router.py` log dosyasından `request_id` arama) konusunda bilgilendirilmesi.

## Kabul Kriterleri
- Dashboard kartı `replan_bridge` verilerini en son log satırına göre gösteriyor ve “approval_request.status”/“analysis.status” ayrıntılarını içeriyor.
- Dokümanda canlıda yaşanabilecek hata senaryoları (callback gelmiyor, log bozuk, approval hızlı reddediyor) maddelenmiş ve çözüm adımları yazılmış.
- Bu plan dosyasındaki adımlar Trello/Jira/README gibi yerlerde referans verilmek üzere kısa görevler olarak ayrıştırılmış (istenirse `NEXT_ACTION.md` güncellenebilir).

## Sonraki Adımlar (örnek)
1. Dashboard kartını genişletip `build_status_payload`’a `replan_bridge` verilerini ekle (tamamlandı ama görsel gösterim ve API endpoint’i test et). Sağlık verisi olarak `latest_status` (ok/error) vurgulanmalı.
2. Dokümanın 5. bölümüne canlıya geçiş kontrol listesini ekle; `docs/phase263_replan.md`’de halihazırda bir paragraf varsa, canlıya alım kurallarını maddeler halinde yeniden yaz.
3. Operasyon ekibinden bir kişiye `replan` bus’ını anlat ve `approval_request` ID’leri/Telegram callback’leri üzerinden canlıya nasıl müdahale edileceğini göster.
4. Phase 263 sonrası raporunu `memory/2026-03-11.md` ve `CURRENT_STATE.md`/`NEXT_ACTION.md` üzerinden güncelleyip Phase 264 planına referans ver.

Hazırsan bu planı geliştirmeye devam edebilir, Dashboard için kısa bir taslak JSON da yazabilir ya da canlıya alma adımlarını (örn. `deploy_phase263.sh`) detaylandırabilirim. Hangi kısmı açmamı istersin?