# Phase 204 Plan — İnsan Onay Mekanizması

Bu belge Phase 204’teki insan onay mekanizmasını sistematik biçimde kurmak için uygulanacak adımları listeler. Onay sistemi:
1. Kritik komut/alarm durumlarını tanıyacak,
2. Telegram/e-posta üzerinden onay istekleri gönderecek, 
3. Onay/red cevabını workflow_engine/planning akışına iletecek, 
4. Onaysız yürütmeleri durduracak veya rollback yapacak.

## Ana bileşenler
- **Onay sınıflandırması:** `policies/`, `workflows/` ve `core/orchestrator` içinden hangi eylemlerin onay gerektirdiğini çıkar. Bunları JSON/Markdown tabanlı bir `approval_registry` içinde tut.
- **Approval engine:** Yeni `approval` modülü (`core/approval.py` gibi) onay, beklemede, reddedildi durumlarını yönetir; EventBus üzerinden `EventTypes.TASK_CREATED`, `TASK_FAILED`, `NODE_DEAD` gibi olaylara hook sağlar.
- **Bildirim:** `monitor/telegram_alert.py` ile Telegram'a onay isteği gönder. Gerekirse `monitor/email_alert.py` (yeni) ile e-posta. Yanıtları dinleyip EventBus üzerinden `EventTypes.TASK_CREATED` yenileme/continue olayına çevir.
- **Workflow entegrasyonu:** `core/orchestrator.py` içerisinde onay bekleyen işlemleri durdur/güncelle; onay alınca `EventTypes.WORKFLOW_STARTED`/`WORKFLOW_COMPLETED` akışını güncelle.
- **Test & validation:** `tests/test_approval_flow.py` ve sahte Telegram cevaplarını simüle eden bir harness yaz.

## Chunk stratejisi
1. `phase204/01-requirements.md` – onay gerektiren durumlar ve `approval_registry` tasarımı.
2. `phase204/02-engine.md` – approval state machine, eventbus hook’ları ve dispatcher davranışı yazılır ve belgelenir.
3. `phase204/03-notifications.md` – Telegram/e-posta kanalı güncellemeleri, onay mesaj formatı ve yanıt işleme süreci.
4. `phase204/04-validation.md` – test setleri, örnek CLI komutları, `tests/test_approval_flow.py`.

## İlk adımlar
- `policies/shell_policy.py` ve `workflows/` içindeki eylemleri tarayarak bir onay listesi derle.
- `core/approval.py` skeleton (ApprovalRequest, ApprovalState, ApprovalManager) oluştur.
- EventBus abone olmadan önce `approval_registry` dosyasını `planning/phase204_approval.md` içinde belgeleyip `CURRENT_STATE.md`'de Phase 204’ü güncelle.

İlerledikçe adımları ticket olarak ✅/🟡 olarak işaretler, kısa rapor ve ilgili dosya yollarını sana gönderirim.
## Validation updates
- Added phase204/validation_runner.py + IMMEDIATE_VALIDATION.md for manual approval checks.
- Added tests/test_approval_wait.py to exercise ApprovalManager.wait_for_status.
