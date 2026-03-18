# FINAL HANDOFF — GRAYWOLF

Tarih: 2026-03-18
Durum: V1.0 çekirdek kapanış baseline tamamlandı.

## Graywolf Nedir?
Stateful, güvenli, gözlemlenebilir ve recoverable bir AI operasyon asistanı.

## Günlük Operasyon (5 komut)
```bash
scripts/graywolf status
scripts/graywolf precheck
scripts/graywolf queue --limit 5
scripts/graywolf approvals
scripts/graywolf report daily
```

## Kritik İşletim Kuralları
- Riskli intent -> approval olmadan ilerleme yok
- Her değişiklik turu -> precheck
- Runtime state/rolling artifact commitlenmez

## Final Artefaktlar
- Closure baseline: `reports/CLOSURE_BASELINE_2026-03-18.md`
- Acceptance: `reports/CLOSURE_ACCEPTANCE_2026-03-18.md`
- Release packet: `reports/PROJECT_RELEASE_PACKET_2026-03-18.md`

## Not
Repo hijyeninde archive-intake yaklaşımı kullanıldı; silme yerine izlenebilir taşıma tercih edildi.
