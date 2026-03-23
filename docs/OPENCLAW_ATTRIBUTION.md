# OpenClaw Attribution (Graywolf Migration)

Bu belge, Graywolf içinde OpenClaw kaynaklı kod/uyarlama kullanımı için lisans ve attribution çerçevesini tanımlar.

## Upstream project
- Project: OpenClaw
- Source: https://github.com/openclaw/openclaw
- Docs mirror: https://docs.openclaw.ai
- License: MIT
- Upstream copyright: Copyright (c) 2025 Peter Steinberger

## License compliance policy
Graywolf içinde OpenClaw'dan alınan veya uyarlanan her parça için:
1. Orijinal lisans (MIT) korunur.
2. Copyright + izin metni korunur.
3. Dosya başında veya ilgili dokümanda `Source: openclaw/...` referansı verilir.
4. Uyarlanan parçalarda `Adapted for Graywolf` notu eklenir.

## Required header template (for adapted files)
```text
# Source: OpenClaw (https://github.com/openclaw/openclaw)
# License: MIT
# Adapted for Graywolf
```

## Mapping policy
- `as-is`: OpenClaw dosyası minimal değişiklikle alınır, lisans başlığı korunur.
- `adapted`: Davranış korunur, Graywolf mimarisine uyarlanır; uyarlama notu zorunludur.
- `reference-only`: Kod alınmaz, sadece mimari referans olarak kullanılır.

## Audit checklist (per migration PR)
- [ ] Alınan/uyarlanan dosyaların listesi var
- [ ] Her dosya için source path belirtilmiş
- [ ] MIT lisans metni korundu
- [ ] Attribution dosyası güncellendi
- [ ] Graywolf bağımsız runtime hedefi ihlal edilmedi
