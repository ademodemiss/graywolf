# CLOSURE ACCEPTANCE — 2026-03-18

## Senaryo 1 — Precheck Gate
- Komut: `scripts/graywolf precheck`
- Sonuç: PASS

## Senaryo 2 — Basit Görev (ALLOW)
- Komut: `scripts/graywolf run --intent healthcheck --goal "closure acceptance allow"`
- Beklenen: `queued`
- Sonuç: `queued` ✅

## Senaryo 3 — Approval Gerektiren Görev (CONFIRM)
- Komut: `scripts/graywolf run --intent deploy --goal "closure acceptance confirm"`
- Beklenen: `confirm_required`
- Sonuç: `confirm_required` ✅
- Örnek request_id: `APR-20260318230558-01b231`

## Senaryo 4 — Yasak Görev (DENY / Failure Handling)
- Komut: `scripts/graywolf run --intent disable_guardrails --goal "closure acceptance deny"`
- Beklenen: `denied`
- Sonuç: `denied` ✅

## Senaryo 5 — Log / Report / Monitor
- `scripts/graywolf logs --target daemon --lines 10` ✅
- `scripts/graywolf report daily` ✅
- `scripts/graywolf monitor status` ✅
- `scripts/graywolf status` ✅

## Senaryo 6 — Approval Görünürlüğü
- Komut: `scripts/graywolf approvals`
- Sonuç: pending/granted/denied dağılımı dönüyor ✅

## Sonuç
Acceptance smoke seti v1.0 çekirdek kapsamı için başarılı.
Ham çıktı: `reports/CLOSURE_ACCEPTANCE_RAW_2026-03-18.txt`
