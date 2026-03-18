# PROJECT RELEASE PLAN V1 — 2026-03-18

## Goal
Graywolf v1.0 çekirdeğini release seviyesine getirmek: asistan deneyimi + güvenli execution motoru.

## Scope (V1.0)
- intent -> task/job
- queue + runner
- execution layer (terminal/script/tool/api)
- approval/policy
- logging/observability
- precheck/health/status/report
- failure handling/recovery temel akışı
- README + canonical + operations + CLI docs tutarlılığı

## Out of Scope (Deferred)
- multi_agent kapsamı
- phase notu/deneysel planning katmanları
- ürün çekirdeğine katkısı olmayan demo/artefakt yükü

## Phase Plan
1. **F0 Reality & Baseline**
   - CLOSURE_BASELINE raporu üretildi.
2. **F1 Freeze & Core Stabilization**
   - Sadece stabilizasyon/hizalama/no-break düzeltmeler.
3. **F2 Repo Hygiene**
   - keep/archive/drop-review sınıflandırma ve taşıma planı.
4. **F3 Documentation Consolidation**
   - README, PROJECT_CANONICAL_STATE, OPERATIONS, CLI_COMMANDS tek gerçek kaynak.
5. **F4 Acceptance**
   - precheck + run + approval + failure + logs/report + monitor/status.
6. **F5 Release Packet**
   - final handoff + release packet + kalan defer listesi.

## Deliverables
- reports/CLOSURE_BASELINE_2026-03-18.md
- reports/DROP_REVIEW_LIST.md
- reports/CLOSURE_ACCEPTANCE_2026-03-18.md
- reports/PROJECT_RELEASE_PACKET_2026-03-18.md
- reports/FINAL_HANDOFF_GRAYWOLF.md

## Decision Rules
- Emin değilsek silme yok; drop-review listesine al.
- Runtime dosyası değiştiyse test + precheck zorunlu.
- Küçük, geri döndürülebilir commitler.
