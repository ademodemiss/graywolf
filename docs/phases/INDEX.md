# Phases Index (Canonical)

Bu index, phase dokümanlarını tek yerden takip etmek için oluşturuldu.

## ACTIVE (ürün akışına bağlı)
- V1.0 çekirdeği için phase dokümanları aktif yürütme kaynağı değildir.
- Aktif operasyon kaynağı: `docs/PROJECT_CANONICAL_STATE.md` ve `docs/ops/OPERATIONS.md`.

## ARCHIVE (tamamlanmış/geçmiş)
- Phase plan/dokümanları Wave-2 ile archive intake altına taşındı:
  - Planlar: `docs/ops/archive/intake_wave2/planning/phase*.md`
  - Monitoring docs: `docs/ops/archive/intake_wave2/docs_phases/phase*_monitoring.md`
  - Replan doc: `docs/ops/archive/intake_wave2/docs_phases/phase263_replan.md`

## Üretilen Makine Raporu
- `reports/phase_index.json`

## Kural
- Yeni phase eklendiğinde önce burası güncellenir.
- Aktif/Archive kararı burada tek kaynaktır.
