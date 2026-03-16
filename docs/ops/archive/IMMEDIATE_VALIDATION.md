# Phase 204 — Immediate Validation Checklist

Bu doküman, approval döngüsünün çalışan bir senaryoyla sınanması için gereken adımları içerir.

1. `phase204/validation_runner.py` dosyasını çalıştırarak riskli bir komut için approval akışını tetikleyin:
   ```bash
   python3 -m phase204.validation_runner "mv /tmp/a /tmp/b" --auto grant --delay 0.5
   ```
   Bu komut `ApprovalManager` ile policy kararına göre `EventTypes.APPROVAL_REQUESTED` yayımlar, `ApprovalNotifier` loglara yazar ve `--auto grant` sayesinde otomatik onay yayınlar.
2. Alternatif olarak, otomatik onay yerine manuel olarak onay verin:
   - `run logs/approval_notifier.log` içeriğini kontrol ederek `request_id` tespit edin.
   - Yayılan event’i simüle etmek için: `python3 - <<'PY'` bloğuyla `BUS.publish(EventTypes.APPROVAL_GRANTED, {...})` komutunu çalıştırın.
3. Onay granti geldikten sonra script `Command approved and ready to run.` çıktısını verir. `Denied` senaryosu için `--auto deny` kullanarak benzer şekilde `ApprovalManager`’ın durumu güncellediğini doğrulayın.
4. Gerekirse `phase204/validation_runner.py` içinden `logs/phase204_validation.log` dosyasına bakarak timeout veya hata mesajlarına erişin.

Bu adımlardan sonra Phase 204 validation chunk’ı belgelenmiş ve approval döngüsü CLI/test seviyesinde doğrulanmış olur.