# Post Release Hygiene Final Decisions — 2026-03-18

## KEEP-TRACK (çekirdek/operasyonel)
- `requirements.txt`
- `agent/__init__.py`, `agent/tool_handlers.py`
- `core/cost_tracker.py`
- `dashboard/dashboard_generator.py`
- `self_improve/error_analyzer.py`, `self_improve/repair_loop.py`
- `tools/excel_tool.py`, `tools/graywolf_setup.py`, `tools/self_improve_tool.py`
- `workflows/self_improve_log_analysis.yaml`
- `tests/test_*.py` (operasyon/recovery/approval/tooling doğrulama seti)

## DEFER (local/runtime data)
- `data/` (runtime/generated artefact alanı; commit dışı bırakıldı)

## Not
- Rolling `_latest` raporları commitlenmedi.
- Precheck sonrası karar uygulanmıştır.
