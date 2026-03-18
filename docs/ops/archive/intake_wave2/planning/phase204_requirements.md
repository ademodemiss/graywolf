# Phase 204/01 — Approval Requirements

Bu belge, İnsan Onay Mekanizması için tespit ettiğim temel onay gereksinimlerini ve kategorilerini içeriyor. Onay akışı, aşağıdaki kriterlerdeki eylemleri yakalayacak ve uygun bildirim + karar döngüsünü tetikleyecek.

## Onay Kriterleri
| Kategori | Eylem | Açıklama | Örnek Komutlar |
| --- | --- | --- | --- |
| **Forbidden (red)** | Asla çalıştırılmaz | Sudo/öst beyaz listede değil, opsiyonu yok | `sudo`, `reboot`, `shutdown`, `poweroff`, `init`, `halt`, `rm` |
| **Riskli (onay gerektirir)** | Sistem/FS değişiklikleri | Paket yöneticileri, dosya taşıma, ownership değişimi | `mv`, `cp`, `dd`, `chmod`, `chown`, `apt`, `apt-get`, `npm`, `node` |
| **Zincirli & pipe** | Tek komut hattında birden fazla komut | `&&`, `||`, `;`, `|` kombinasyonları; artı takaslı üst seviye | `echo a && echo b`, `mkdir dir && cd dir` |
| **Bilinmeyen** | policy’de tanımlı değil | ShellPolicy’de listelenmeyen temel komutlar (örneğin `bat` veya `docker`) | `docker`, `terraform plan` (varsa) |
| **Workflow kritik** | workflow_engine içinde hassas eylemler | `workflow_engine` veya `core/orchestrator` içinde belirlenmiş restart, deploy, approve eylemleri | `core/orchestrator --restart`, `workflow_engine dag_executor --run critical` |
| **Alert/incident** | Incident modüllerini tetikleyen komutlar | EventBus üzerinden incident/alert üreten script’ler | `infra/incident_response.py --escalate`, `monitor/recovery_dispatcher.py --run-once` |

## Onay Akışı Notları
- Approval Request üretimi `core/approval.py` içinde sınıflandırıldıktan sonra EventBus (örneğin `EventTypes.APPROVAL_REQUESTED`) ile diğer modüllere duyurulacak.
- Onay gerektiren komutlar hem policy hem orchestrator içinde kontrol edilecek; CLI/agent çağrıları `ApprovalManager.evaluate(command)` aracılığıyla onay gerektiriyor.
- Telegram veya e-posta üzerinden onay olursa EventBus’a `EventTypes.APPROVAL_GRANTED`/`APPROVAL_DENIED` diasını yayınlayacağız; workflow_engine bu olaylara bakacak.

## İlerleme Planı
1. `core/approval.py` oluştur (ApprovalRequest, ApprovalManager, ApprovalState). ApprovalRequest her komut için `id`, `command`, `category`, `requested_by`, `status`, `ts`. ApprovalManager, policy tabanlı sınıflandırma + EventBus publish + bekleme mantığı içerir.
2. `monitor/telegram_alert.py`’yi onay mesajları (inline button) ile genişlet ve `approval_requests.json` gibi geçici kayıt tut.
3. `core/orchestrator.py` içinde approval beklemeleri için `if approval_request.status != ApprovalState.GRANTED: block/hold` ekle.
4. Tests/test_approval_flow ile approval request yarat-to-command pipeline’ını simüle et.

Bu dosyada atladığım bir kritik durum olursa belirt, hemen planı genişletirim.