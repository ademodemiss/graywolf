# Graywolf v2 Canonical Architecture (Graywolf-first)

_Last updated: 2026-03-17_

Kural: Bu mimari Graywolf içindir. Dış sistemler sadece referans olabilir; runtime veya ürün sınırı Graywolf içinde kalır.

## 1) Tek resmi runtime hattı

**Runtime Entry (canonical):**
- `core/autonomous_loop.py`
- Worker çağrısı: `scripts/run_autonomy_worker.py`
- Daemon kontrolü: `scripts/autonomy_daemon.sh`

Bu üçlü dışındaki loop/controller dosyaları canonical değildir.

## 2) Tek resmi workflow execution hattı

**Workflow Executor (canonical):**
- `workflows/runner.py::run_workflow`

Orchestrator entegrasyonu bu fonksiyondan ilerler:
- `core/orchestrator.py -> workflows/runner.py`

`workflow_engine/workflow_executor.py` geçiş döneminde tutulur; yeni akışlarda kullanılmaz.

## 3) Command -> Task -> Response canonical zinciri

1. Command intake (geçici prototip, bağlanacak):
   - `agent/command_parser.py`
   - `agent/task_decomposer.py`
2. Plan/Execution:
   - `core/orchestrator.py`
   - `workflows/runner.py`
3. Güvenlik/Onay:
   - `policies/shell_policy.py`
   - `core/approval.py`
   - `monitor/approval_callback_router.py`
4. Operasyon çıktısı:
   - `logs/*`, `reports/*`

## 4) Çakışma kapatma kararları

### Runtime/loop
- Keep (canonical): `core/autonomous_loop.py`, `scripts/run_autonomy_worker.py`, `scripts/autonomy_daemon.sh`
- Freeze/Deprecate target:
  - `core/full_autonomy.py`
  - `core/full_autonomy_controller.py`
  - `core/agent_loop.py`
  - `core/service_runner.py`

### Workflow
- Keep (canonical): `workflows/runner.py`
- Freeze/Deprecate target:
  - `workflow_engine/workflow_executor.py` (yalnız compatibility/test)

### Prototype layers
- `agent/*`, `goals/*`, `capabilities/*` şu an runtime dışı prototip katmanıdır.
- Karar: ya canonical hatta bağlanır ya `archive/` altına taşınır; arada bırakılmaz.

## 5) v2 tamamlanma kriteri (net)
Tek uçtan şu senaryo tek komutla çalışmalı:
- command al
- task/plan üret
- approval/risk uygula
- execute et
- report/log üret
- state güncelle

## 6) Yakın icra sırası (next 3)
- [x] `workflow_engine/workflow_executor.py` için deprecation notu + import kullanım taraması.
  - Tamamlananlar: kullanım tarandı, `scripts/simulate_approval_flow.py` canonical `workflows.runner` hattına taşındı.
- [x] `core/service_runner.py` ve `core/agent_loop.py` için canonical entry’ye yönlendirme başlangıcı.
  - Tamamlananlar: canonical karar dokümana işlendi, `docs/ops/AUTONOMY_QUICKSTART.md` canonical runtime komutlarına çekildi, `core/phase_smoke.py` importları `core.autonomous_loop`a güncellendi.
- [x] `agent/dispatcher.py` hattını canonical orchestrator zincirine bağlama kararı (bind veya archive) ve tek kararın dokümana işlenmesi.
  - Karar: **archive/freeze**. Canonical execution hattı `core/orchestrator.py` + `workflows/runner.py` olarak kalır.

## 7) İcra logu (işaretlenen tamamlananlar)
- [x] Canonical mimari dosyası üretildi (`docs/GRAYWOLF_V2_CANONICAL_ARCHITECTURE.md`)
- [x] Deprecation matrisi üretildi (`docs/DEPRECATION_MATRIX.md`)
- [x] Kanonik durum dosyası güncellendi (`docs/PROJECT_CANONICAL_STATE.md`)
- [x] Autonomy quickstart canonical hatta taşındı (`docs/ops/AUTONOMY_QUICKSTART.md`)
- [x] Workflow compatibility script canonical executor’a geçirildi (`scripts/simulate_approval_flow.py`)
- [x] Phase smoke importları canonical runtime’a çekildi (`core/phase_smoke.py`)
