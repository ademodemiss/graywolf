# GrayWolf Release Checklist

## Faz 1 — Sistem Temeli
- [x] `policies/shell_policy.py` ALLOW/CONFIRM/DENY + reason
- [x] `tools/terminal_tool.py` shell=False, shlex.split, timeout, JSON log
- [x] `logs/terminal.log` alanları: ts,cwd,cmd,decision,reason,exit_code,duration_ms,stdout_len,stderr_len
- [x] Kanıt testleri: `python3 -c "print('ok')"`, `git status`, `pip --version`, `echo a && echo b` (CONFIRM)

## Faz 2 — Ajan Motoru
- [x] `core/orchestrator.py` goal→plan→execute→evaluate
- [x] retry/backoff ve hata sınıflandırma
- [x] `workflows/runner.py` step timeout + continue_on_error
- [x] `core/llm_factory.py` sağlayıcı seçimi

## Faz 3 — Mail Sistemi
- [x] Draft oluşturma + confirm akışı
- [x] Dry-run gönderim
- [x] Workflow entegrasyonu
- [x] SMTP konfigürasyon kontrolü (`check-smtp`)
- [x] SMTP eksikse fallback: warning + `fallback_dry_run`
- [x] Gerçek SMTP bağlantı testi (`test-smtp`)
- [x] Gerçek mail gönderimi (`send --dry-run false`) başarı kanıtı

## Faz 5 — İki Beyinli LLM Router
- [x] `core/llm_router.py` (primary codex + fallback gemini)
- [x] Retryable hata sınıfları: RateLimit/Timeout/Connection/Provider
- [x] Fallback log: `LLM_ROUTER_FALLBACK primary=codex fallback=gemini ...`
- [x] Orchestrator entegrasyonu (`LLMRouter().get()`)
- [x] Testler: `tests/router_test.py`, `tests/orchestrator_router_test.py`

## Faz 4 — Monitoring / Operability
- [x] `PHASE4.md`
- [x] `workflows/healthcheck.json`
- [x] `workflows/quick-report.json`
- [x] Quick report policy-uyumlu adımlar
- [x] Son kabul smoke + workflow kanıt paketi

## Faz 6 — User Setup Productization
- [x] `PHASE6.md` plan dokümanı
- [x] `tools/provider_setup_wizard.py` (gmail/outlook)
- [x] `tools/provider_validation.py` (missing/invalid/warning)
- [x] `.env.example` provider şablonu
- [x] README kullanıcı kurulum adımları

## Faz 7 — Monitoring Core
- [x] `monitor/heartbeat.py`
- [x] `monitor/alert.py`
- [x] `monitor/status_report.py`
- [x] idle/agent_loop/workflow_error alarm üretimi
- [x] `python3 -m monitor.heartbeat --test` doğrulaması

## Faz 8 — Telegram Alert & Status
- [x] `monitor/telegram_alert.py`
- [x] `send_telegram_message(text)` (Bot API)
- [x] TELEGRAM env eksikse güvenli fallback (`TELEGRAM_NOT_CONFIGURED`)
- [x] heartbeat + alert Telegram entegrasyonu
- [x] `python3 -m monitor.telegram_alert --test` doğrulaması

## Faz 9 — Web Dashboard
- [x] `dashboard/` klasörü ve dosyaları (`server.py`, `views.py`, `data.py`, `templates/index.html`, `static/style.css`)
- [x] `/api/status` JSON endpoint
- [x] `/` tek sayfa dashboard
- [x] `python3 -m dashboard.server --test` doğrulaması
- [x] terminal.log kanıtı

## Faz 11 — Self-Improvement Engine
- [x] `self_improve/code_analyzer.py`
- [x] `self_improve/improvement_engine.py`
- [x] `self_improve/patch_generator.py`
- [x] `self_improve/review_loop.py`
- [x] `python3 -m self_improve.code_analyzer` doğrulaması

## Faz 12 — Plugin System
- [x] `plugins/plugin_loader.py`
- [x] örnek pluginler: `system_tools`, `file_tools`, `network_tools`, `report_tools`
- [x] `python3 -m plugins.plugin_loader` doğrulaması

## Faz 13 — Memory System
- [x] `memory/memory_store.py`
- [x] `memory/memory_search.py`
- [x] `memory/memory_index.py`
- [x] `python3 -m memory.memory_store` doğrulaması

## Faz 14 — Long-Running Agent Loop
- [x] `core/agent_loop.py`
- [x] goal→plan→execute→monitor→report döngüsü
- [x] idle alert + telegram status entegrasyonu
- [x] `python3 -m core.agent_loop --goal 'healthcheck system' --once` doğrulaması

## Faz 22 — Ops Monitoring + Alerts
- [x] `post_release/ops_config.py` + ENV override (`GW_DISK_*`, `GW_LOG_*`, `GW_LOAD_*`)
- [x] `post_release/ops_monitor.py` (disk/load/log/memory, `ok|warn|error`)
- [x] `post_release/alerts.py` (stdout default, Telegram/Webhook opsiyonel)
- [x] `post_release/ops_smoke.py --test` (`error` fail, `ok/warn` pass)

## Faz 23–26, 28–30 — Ops Smoke Gates
- [x] `post_release/phase_smoke.py` ile faz smoke doğrulamaları
- [x] Phase 23/24/25/26/28/29/30 `--test` komutları `exit_code:0`

## Faz 27 — Local Health Endpoint
- [x] `post_release/health_server.py` sadece `127.0.0.1:8899` bind
- [x] `/health` self-test kanıtı (`python3 -m post_release.health_server --self-test`)

## Release Öncesi Son Kontrol
- [ ] `python3 -m py_compile` (değişen dosyalar)
- [ ] `python3 -m tests.smoke`
- [ ] `python3 -m workflows.runner --file workflows/healthcheck.json`
- [ ] `python3 -m workflows.runner --file workflows/quick-report.json`
- [ ] terminal.log son koşularının arşivlenmesi

## Rollback
1. Son stabil commit/tag'e dön.
2. `logs/terminal.log` ile hata komutlarını incele.
3. SMTP/env değişikliklerini geri al.
4. Smoke + healthcheck koşup sistemi tekrar doğrula.
