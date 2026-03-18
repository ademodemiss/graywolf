# Repo Hygiene Wave-2 Plan

Tarih: 2026-03-18
Durum: Uygulama öncesi plan (no-break)

## Amaç
Working tree gürültüsünü azaltmak ve v1.0 çekirdeği dışındaki kalıntıları izlenebilir şekilde ayırmak.

## Keep (çekirdek)
- `core/*` (runtime/queue/session/approval)
- `scripts/*` (worker/daemon/precheck/operator)
- `policies/*`
- `monitor/*` (approval/recovery/replan)
- `workflows/runner.py`
- `core/graywolf_cli.py`, `scripts/graywolf`
- çekirdek testler (`tests/test_v2_runtime_foundation.py`, `tests/test_agent_command_chain.py`)

## Archive (history/phase/artifact)
- `planning/phase*.md`
- `docs/phase*_monitoring.md`
- `verification/*`
- rolling report artifactleri (`reports/*_latest.md`) — git dışı/artefact
- geçmiş/moved stub dosyaları (`CURRENT_STATE.md`, `NEXT_ACTION.md`, `ROADMAP.md`) — referans stub olarak bırakılabilir

## Drop-Review
- `reports/DROP_REVIEW_LIST.md` dosyasındaki adaylar

## Uygulama Sırası
1. Referans taraması (`rg`) ile drop-review adaylarını doğrula
2. Archive adaylarını `docs/ops/archive/intake_wave2/` altında gruplandır
3. Precheck çalıştır
4. Küçük commitlerle ilerle
