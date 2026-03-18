# RELEASE DECISION — 2026-03-18

## Karar
**APPROVED (v1.0 baseline)**

## Gerekçe
- Runtime omurga aktif ve çalışır (queue/runner/execution/approval/policy)
- `scripts/graywolf precheck` PASS
- Acceptance smoke seti PASS (`reports/CLOSURE_ACCEPTANCE_2026-03-18.md`)
- Doküman tek kaynak seti konsolide edildi (README + canonical + operations + CLI)
- main/task/origin senkron
- CI `release-precheck` (main) success

## Bilinçli Risk / Not
- Çalışma ağacında local modified/untracked gürültü mevcut (operasyonel blocker değil, hygiene backlog)
- Node 20 deprecation uyarısı CI annotation olarak görünüyor (blocker değil)

## Sonraki Aksiyon
- Post-release hygiene dalgası (local noise cleanup) ayrı no-break turda yürütülecek.
