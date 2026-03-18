# Phase 263 – Replan Notifications ve Approval Bridge

Bu belge Phase 263 kapsamında kurulmuş `REPLAN_READY`/`REPLAN_EXECUTED` olaylarının SelfImprove analizi ve Telegram onay hattına bağlanmasını açıklar.

## 1. Amaç
* `monitor/replan_notifier.py` tarafından yayılan replan olaylarını `self_improve` döngüsüne taşıyıp, LLM önerileriyle birlikte Telegram onayına sunmak.
* Onaylayıcı yanıtların `monitor/approval_callback_router.py` üzerinden `EventTypes.APPROVAL_*` olarak tekrar yayımlanması sayesinde `ApprovalManager` tabanlı gate'lemeyi korumak.

## 2. Akış
1. `EventBus` üzerinde `EventTypes.REPLAN_READY` veya `REPLAN_EXECUTED` olayları yayımlanır.
2. `monitor/replan_self_improve_bridge.py` bu olayları dinler, `SelfImproveTool` ile `replan_notifier.log` ölçümlerini özetler, analiz eder ve Telegram string raporu hazırlar.
3. Aynı yerde Phase 204'ten miras `ApprovalManager` ile `replan` kategorisinde yeni `ApprovalRequest` doğar ve `Approval talebi: <request_id>` satırı mesajda görünür.
4. Telegram üzerindeki inline “Onayla ✅” / “Reddet ❌” düğmeleri `monitor/approval_callback_router.py` tarafından `EventTypes.APPROVAL_GRANTED`/`DENIED` olaylarına dönüştürülür; `ApprovalManager` bu olayları dinleyip `request` statüsünü günceller.
5. `self_improve_replan.log` her olay için JSON satır içerir; bridge bu loga `analysis` ve `approval_request` bilgilerini yazar.

## 3. Telegram mesaj şablonu
```text
[Replan {event_type}] workflow={workflow_name}
Replan özeti:
{summary}
SelfImprove önerisi:
{analysis_text}
Analiz durumu: {status}
Approval talebi: {request_id} (durum: {status})
```

Düğmeler callback_data olarak `approval.grant:<request_id>` / `approval.deny:<request_id>` gönderir (TB: `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` ortam değişkenleri olmalı).

## 4. Log ve dashboard gözlemleri
* `logs/self_improve_replan.log` her analiz için `{event, payload, analysis, approval_request}` şeklinde JSON içerir.
* `dashboard/data.py` artık logu okuyup son replan olayını, toplam sayıyı ve approval statüsünü `build_status_payload` içine taşıyor (güncelleme dokümanda da referans verilmiştir).

## 5. Testler
```bash
.venv/bin/python -m pytest tests/test_self_improve_tool.py tests/test_self_improve_orchestrator.py tests/test_replan_notifier.py tests/test_replan_self_improve_bridge.py
```
Bu komut 11 testi çalıştırır ve replan bridge + approval entegrasyonunu doğrular.

## 6. Canlıya alma notları
1. `TELEGRAM_BOT_TOKEN` ile `TELEGRAM_CHAT_ID` ortam değişkenleri production ortamda ayarlanmalı.
2. `ApprovalCallbackRouter` log dosyasına yazılan `request_id`'ler, Telegram mesajları üzerinden takip edilmeli.
3. Dashboard `replan_bridge` alanı (dashboard/data.py) 20 log satırını kontrol ederek en son olayın `event` ve `approval_request.status` değerini sunar.
