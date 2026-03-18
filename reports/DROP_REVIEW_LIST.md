# DROP REVIEW LIST (Wave-2)

Tarih: 2026-03-18
Kural: Bu listedeki dosyalar **hemen silinmez**. Önce referans/iş değeri doğrulanır.

## Adaylar
- `analysis/plan_validator.py`
- `deployment/README.md`
- `requirements.txt`
- `self_improve/error_analyzer.py`
- `self_improve/repair_loop.py`
- `tasks/code/`
- `tasks/examples/phase251_readme_installation.json`

## Değerlendirme ölçütü
- Runtime veya operasyonel komut zincirinde aktif referans var mı?
- V1.0 çekirdeğine doğrudan katkı sağlıyor mu?
- Sadece tarihsel/deneysel yük mü?

## Karar kuralları
- Emin değilsek DROP yapılmaz, archive veya keep'e alınır.
- DROP kararı öncesi `rg` referans taraması + precheck tekrarı zorunlu.

## Wave-2 Karar Güncellemesi (2026-03-18)
- `requirements.txt` -> KEEP
- `self_improve/error_analyzer.py` -> KEEP
- `self_improve/repair_loop.py` -> KEEP
- `deployment/README.md` -> ARCHIVE (`docs/ops/archive/intake_wave2/deployment/README.md`)
- `tasks/code/` -> ARCHIVE (`docs/ops/archive/intake_wave2/tasks/code`)
- `tasks/examples/phase251_readme_installation.json` -> ARCHIVE (`docs/ops/archive/intake_wave2/tasks/examples/phase251_readme_installation.json`)
- `analysis/plan_validator.py` -> ARCHIVE (`docs/ops/archive/intake_wave2/analysis/plan_validator.py`)
