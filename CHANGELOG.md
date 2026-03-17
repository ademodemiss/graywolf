# Changelog

## [Unreleased] - 2026-03-05

### Added
- Post-release operasyon paketi (Phase 22–30):
  - `post_release/ops_config.py` (ENV override + güvenli default limitler)
  - `post_release/ops_monitor.py` (disk/load/log/memory WARN/ERROR kontrolleri)
  - `post_release/alerts.py` (stdout + Telegram/Webhook opsiyonel stub, `delivery_skipped` raporu)
  - `post_release/ops_smoke.py` (ok/warn pass, error fail + dry delivery doğrulaması)
  - `post_release/health_server.py` (yalnızca `127.0.0.1:8899` bind, `/health` self-test)
  - `post_release/phase_smoke.py` (Phase 23/24/25/26/28/29/30 smoke)
- `core/agent_loop.py` requirements haritası Phase 22–30 için proof-gated komutlarla genişletildi.

### Changed
- `docs/roadmap.md` duplicate `Phase 21` kaydı temizlendi.
- Roadmap’e Phase 22–30 tanımları eklendi.

### Verified
- `python3 -m py_compile /home/adem/graywolf/core/agent_loop.py /home/adem/graywolf/post_release/ops_config.py /home/adem/graywolf/post_release/ops_monitor.py /home/adem/graywolf/post_release/alerts.py /home/adem/graywolf/post_release/ops_smoke.py /home/adem/graywolf/post_release/health_server.py /home/adem/graywolf/post_release/phase_smoke.py`
- `python3 -m post_release.ops_smoke --test`
- `python3 -m post_release.health_server --self-test`
- `python3 -m post_release.phase_smoke --phase 23 --test`
- `python3 -m post_release.phase_smoke --phase 24 --test`
- `python3 -m post_release.phase_smoke --phase 25 --test`
- `python3 -m post_release.phase_smoke --phase 26 --test`
- `python3 -m post_release.phase_smoke --phase 28 --test`
- `python3 -m post_release.phase_smoke --phase 29 --test`
- `python3 -m post_release.phase_smoke --phase 30 --test`
- `python3 -m core.agent_loop --dry-run` _(legacy/deprecated path; canonical runtime: `scripts/run_autonomy_worker.py` + `scripts/autonomy_daemon.sh`)_

## [Unreleased] - 2026-03-04

### Added
- `tools/mail_tool.py`
  - SMTP çözümleme yardımcı fonksiyonu (`_resolve_smtp`)
  - `test-smtp` aksiyonu (bağlantı + login testi)
  - `check-smtp` artık hata yerine `warning` + `fallback: dry_run` döndürüyor
- `RELEASE_CHECKLIST.md` başlangıç sürümü

### Changed
- `send_draft` davranışı:
  - SMTP env eksikse artık hard error yerine `send_simulated` + `mode: fallback_dry_run`
  - Eksik alanlar `missing` listesiyle raporlanıyor

### Added
- `core/llm_router.py`
  - Primary/Fallback router (codex -> gemini)
  - Retryable error normalization: `RateLimitError`, `TimeoutError`, `ConnectionError`, `ProviderError`
  - Fallback event log: `LLM_ROUTER_FALLBACK ...`
- `tests/router_test.py` (rate-limit fallback simülasyonu)
- `tests/orchestrator_router_test.py` (orchestrator + router entegrasyon testi)

### Changed
- `core/orchestrator.py` artık doğrudan provider yerine `LLMRouter().get()` üzerinden LLM alıyor.
- Gmail SMTP canlı gönderim doğrulandı; draft `20260304_052337_255897` başarıyla `sent` durumuna geçti.

### Verified
- `python3 -m py_compile /home/adem/graywolf/tools/mail_tool.py`
- `python3 -m py_compile /home/adem/graywolf/core/llm_router.py /home/adem/graywolf/core/orchestrator.py /home/adem/graywolf/tests/router_test.py /home/adem/graywolf/tests/orchestrator_router_test.py`
- `python3 -m tests.router_test --simulate-rate-limit`
- `python3 -m tests.orchestrator_router_test`
- `python3 /home/adem/graywolf/tools/mail_tool.py --action check-smtp`
- `python3 /home/adem/graywolf/tools/mail_tool.py --action test-smtp`
- `python3 /home/adem/graywolf/tools/mail_tool.py --action send --draft-id 20260304_052337_255897 --dry-run false`
- `python3 -m workflows.runner --file /home/adem/graywolf/workflows/quick-report.json`

### Added
- `PHASE6.md` (user-setup productization roadmap)
- `tools/provider_setup_wizard.py` (gmail/outlook config scaffold, secret masking)
- `tools/provider_validation.py` (provider-based env validation)
- `.env.example` provider templates
- `monitor/heartbeat.py`, `monitor/alert.py`, `monitor/status_report.py` (Faz 7 core monitoring)
- `monitor/telegram_alert.py` (Telegram send + safe no-config fallback)

### Changed
- `tools/mail_tool.py` gains `--action validate-provider --provider <gmail|outlook>` integration.
- Monitoring alerts now trigger Telegram sender via `monitor.alert`.
- Heartbeat now emits Telegram status message using monitoring report formatter.

### Verified
- `python3 -m py_compile /home/adem/graywolf/tools/provider_setup_wizard.py /home/adem/graywolf/tools/provider_validation.py /home/adem/graywolf/tools/mail_tool.py`
- `python3 /home/adem/graywolf/tools/provider_setup_wizard.py --provider gmail --format env`
- `python3 /home/adem/graywolf/tools/provider_setup_wizard.py --provider outlook --format env`
- `python3 /home/adem/graywolf/tools/mail_tool.py --action validate-provider --provider gmail`
- `python3 -m tests.provider_validation_test`
- `python3 -m tests.provider_validation_outlook_test`
- `python3 -m py_compile /home/adem/graywolf/monitor/heartbeat.py /home/adem/graywolf/monitor/alert.py /home/adem/graywolf/monitor/status_report.py /home/adem/graywolf/monitor/telegram_alert.py`
- `python3 -m monitor.heartbeat --test`
- `python3 -m monitor.telegram_alert --test`

### Added
- `dashboard/server.py`, `dashboard/views.py`, `dashboard/data.py`
- `dashboard/templates/index.html`, `dashboard/static/style.css`
- FastAPI + Jinja2 tabanlı tek sayfa durum paneli
- Endpointler:
  - `GET /` (HTML dashboard)
  - `GET /api/status` (JSON status payload)

### Verified
- `python3 -m py_compile /home/adem/graywolf/dashboard/server.py /home/adem/graywolf/dashboard/views.py /home/adem/graywolf/dashboard/data.py`
- `python3 -m dashboard.server --test`

### Added
- `self_improve/code_analyzer.py`, `self_improve/improvement_engine.py`, `self_improve/patch_generator.py`, `self_improve/review_loop.py`
- `plugins/plugin_loader.py` + örnek plugin paketleri (`system_tools`, `file_tools`, `network_tools`, `report_tools`)
- `memory/memory_store.py`, `memory/memory_search.py`, `memory/memory_index.py`
- `core/agent_loop.py` (long-running orchestration loop)

### Changed
- GrayWolf akışı Faz 11→12→13→14 roadmapine göre çok bileşenli otonom yapıya genişletildi.

### Verified
- `python3 -m py_compile /home/adem/graywolf/self_improve/code_analyzer.py /home/adem/graywolf/self_improve/improvement_engine.py /home/adem/graywolf/self_improve/patch_generator.py /home/adem/graywolf/self_improve/review_loop.py`
- `python3 -m self_improve.code_analyzer`
- `python3 -m py_compile /home/adem/graywolf/plugins/plugin_loader.py /home/adem/graywolf/plugins/system_tools/plugin.py /home/adem/graywolf/plugins/file_tools/plugin.py /home/adem/graywolf/plugins/network_tools/plugin.py /home/adem/graywolf/plugins/report_tools/plugin.py`
- `python3 -m plugins.plugin_loader`
- `python3 -m py_compile /home/adem/graywolf/memory/memory_store.py /home/adem/graywolf/memory/memory_search.py /home/adem/graywolf/memory/memory_index.py`
- `python3 -m memory.memory_store`
- `python3 -m memory.memory_index`
- `python3 -m py_compile /home/adem/graywolf/core/agent_loop.py`
- `python3 -m core.agent_loop --goal 'healthcheck system' --once` _(legacy/deprecated path; canonical runtime: `scripts/run_autonomy_worker.py` + `scripts/autonomy_daemon.sh`)_
