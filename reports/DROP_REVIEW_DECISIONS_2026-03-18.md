# Drop Review Decisions — 2026-03-18

| Aday | Ref Count | Karar | Gerekçe |
|---|---:|---|---|
| `analysis/plan_validator.py` | 0 | **DROP-REVIEW** | çekirdek hatta doğrudan referans yoksa opsiyonel |
| `deployment/README.md` | 0 | **ARCHIVE** | dokümantasyon amaçlı, runtime dependency değil |
| `requirements.txt` | 2 | **KEEP** | standard dependency manifest; v1 packaging için gerekli |
| `self_improve/error_analyzer.py` | 3 | **KEEP** | replan/recovery zinciriyle ilişkili modül |
| `self_improve/repair_loop.py` | 1 | **KEEP** | replan/recovery zinciriyle ilişkili modül |
| `tasks/code` | 0 | **ARCHIVE** | runtime çekirdeğinde aktif referans görünmüyor |
| `tasks/examples/phase251_readme_installation.json` | 0 | **ARCHIVE** | runtime çekirdeğinde aktif referans görünmüyor |

## Örnek Referanslar (ilk 3)

### analysis/plan_validator.py
- karar: DROP-REVIEW
- ref_count: 0
- referans bulunamadı

### deployment/README.md
- karar: ARCHIVE
- ref_count: 0
- referans bulunamadı

### requirements.txt
- karar: KEEP
- ref_count: 2
- README.md:192:    pip install -r requirements.txt
- scripts/run_phase_251.py:67:    pip install -r requirements.txt

### self_improve/error_analyzer.py
- karar: KEEP
- ref_count: 3
- docs/roadmap.md:15:- Deliverables: self_improve/error_analyzer.py, self_improve/repair_loop.py, retry policy entegrasyonu, repair evidence report
- docs/roadmap.md:76:*   **Deliverables:** `self_improve/error_analyzer.py` modülünün genişletilmesi, `core/orchestrator.py`'ye "re-plan" (yeniden planla) mantığının eklenmesi.
- docs/roadmap.md:79:    1. `self_improve/error_analyzer.py` içinde hata sebebini sınıflandıran bir helper yaz (örneğin `classify_failure`) ve bu sınıfı `replan_hint` olarak döndüren küçük testler oluştur.

### self_improve/repair_loop.py
- karar: KEEP
- ref_count: 1
- docs/roadmap.md:15:- Deliverables: self_improve/error_analyzer.py, self_improve/repair_loop.py, retry policy entegrasyonu, repair evidence report

### tasks/code
- karar: ARCHIVE
- ref_count: 0
- referans bulunamadı

### tasks/examples/phase251_readme_installation.json
- karar: ARCHIVE
- ref_count: 0
- referans bulunamadı
