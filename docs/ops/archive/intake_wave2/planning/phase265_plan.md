# Phase 265 – Approval Sonrası SelfImprove Otomasyonu

## Amaç
Phase 264’te canlıya alınmaya hazırlanan `ReplanSelfImproveBridge`’in approval ve analiz verilerini temel alarak, **`ApprovalManager` üzerinden `GRANTED` statüsüne ulaşmış replan analizlerini otomatik self-improve görevlerine dönüştürmek**. Bu faz, onaylanan geri bildirimleri insan müdahalesi olmadan LLM destekli düzeltme/iyileştirme işlerine çevirmek ve geri bildirim zincirinin sürekli öğrenme döngüsünü tamamlamak için tasarlandı.

## Hedeflenen bileşenler
1. **`SelfImproveTool` genişletmesi:** `analyze_logs_for_improvements` çıktısı ve `approval_request` metadata’sı baz alınarak, `approval_request.status == "GRANTED"` olan entry’leri `self_improve` görevlerine çevirecek yeni yöntem (örn. `improve_from_replan_entries`). Bu metod, log özetini, workflow adını ve approval metadata’sını alarak otomatik `self_improve` job tanımları çıkarmalı.
2. **Otomasyon döngüsü:** Onaylanan replanları toplayıp sıraya alan bir `monitor/replan_self_improve_scheduler.py` – bu modül `logs/self_improve_replan.log`’dan `GRANTED` entry’leri tarar, önceki run’lardan tekrar işlemeyen entry’leri (örneğin `processed` flag) belirler ve `SelfImproveTool`’un yeni fonksiyonunu kullanarak job başlatır.
3. **Güvenlik & gözlem:** `ApprovalManager`’a bağlı olarak `EventTypes.APPROVAL_GRANTED` olayına tanıklık eden bir `confidence` metriği gerekir. `monitor/approval_health.py` içine bir `approval_latency` metriği eklenip `dashboard/data.py`/templates’te onay bekleme süresi görseli eklensin; ayrıca approval latencysinin 2 dakikayı aşması durumunda ops’a işaret.
4. **Okunabilir log & kanıt:** `logs/self_improve_replan.log` içeriğine `processed_by_phase265` benzeri bir bayrak ekleyerek hangi entry’lerin otomatik self-improve’a dönüştüğünü not edin. `monitor/replan_self_improve_bridge.py` bu flag’ı set edip logu güncelleyen bir helper çağırmalı.

## Kabul kriterleri
* `SelfImproveTool` lokasyonunda `improve_from_replan_entries` (veya benzeri) bir yöntem yazılmış, unit testi (örn. `tests/test_self_improve_tool.py` içine yeni fixture ya da test) ile onaylanmış durumda.
* `monitor/replan_self_improve_scheduler.py` içinde her `GRANTED` entry için bir `self_improve` job oluşturan döngü var; bir entry bir kez işlendiğinde logda `processed_by_phase265` setleniyor.
* `dashboard` ve `monitor/approval_health.py` artık approval latency ve otomasyon durumu (kaç entry işlendi, kaç bekliyor) gösterebiliyor. `dashboard/templates/index.html`’e `replan_bridge_processed` paneli düşünülebilir.
* Phase 265 otomasyonunu tetikleyen entegrasyon testleri (`tests/test_replan_self_improve_scheduler.py` gibi) yazılmış ve `.venv/bin/python -m pytest ...` ile çalıştırılabiliyor.

## Örnek akış
1. `REPLAN_READY` olayı gelince `ReplanSelfImproveBridge` loglara entry yazıyor ve approval request oluşturuyor.
2. `ApprovalManager` inline Telegram onayı sonrası `EventTypes.APPROVAL_GRANTED` yayımlıyor; `monitor/approval_callback_router.py` bu olayı logluyor, approval status `GRANTED` olarak güncelleniyor.
3. `monitor/replan_self_improve_scheduler.py` belirli aralıklarla `logs/self_improve_replan.log`’u tarayıp onaylı entry’leri topluyor (henüz `processed_by_phase265` olmayanlar). Her entry için `SelfImproveTool.improve_from_replan_entries` veya benzeri bir helper çalıştırarak bir self-improve job başlatıyor.
4. Başlatılan job için `logs/self_improve_replan.log`’da `processed_by_phase265: <ts>` ekliyor ve `dashboard/data.py`’ın `replan_bridge` bölümüne `processed_count`, `pending_count` gibi alanlar ekleniyor.

## Sonraki adımlar
1. `SelfImproveTool` içinde `improve_from_replan_entries`’i yaz, `tests/test_self_improve_tool.py`’a/mockla bir test ekle.
2. `monitor/replan_self_improve_scheduler.py` dosyasını oluştur; Cron veya event tabanlı yürütme (örn. `workflow_engine` üzerinden periyodik tetikleme) yapabilir. Auto job queue kaydını `logs/self_improve_replan.log` ile senkronize et.
3. `dashboard` tarafında Phase 265 otomasyonu için `replan_bridge_processed` paneli, `approval_latency` ve `processed`/`pending` sayılarını gösteren bir bölüm oluştur; template + API payload’ı genişlet.
4. `monitor/approval_health.py`’a yeni `processed_count` raporu ekle; ops kanalına `python monitor/approval_health.py --summary` gibi bir komutla Phase 265 otomasyon durumunu gösterecek bir çıktı yaz.
5. Yakında yapılacak değişikliği `memory/2026-03-11.md`’e not et (append) ve `CURRENT_STATE.md`/`NEXT_ACTION.md`’ı Phase 265’e göre güncelle.

Hazırsan bu planı yürütmeye başlarım — ilk olarak `SelfImproveTool`’a otomasyon fonksiyonunu ekleyeyim mi, yoksa scheduler + dashboard kısmına geçelim mi?