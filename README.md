# Graywolf

Graywolf, bilgisayar veya VPS üzerinde 7/24 çalışabilen, doğal dil niyetini güvenli şekilde icraya çeviren bir AI operasyon asistanıdır.

> ChatGPT konuşur, Graywolf işi yapar.

## V1.0 Ürün Tanımı
Graywolf iki katmandan oluşur:
1. **Assistant Experience**: kullanıcı niyetini anlar, sonucu anlaşılır biçimde sunar.
2. **Execution Runtime**: intent → policy → queue → runner → rapor akışını işletir.

## V1.0 Kapsamı
- intent -> task/job
- queue + runner
- execution (terminal/script/tool)
- approval/policy (ALLOW/CONFIRM/DENY)
- logging/observability
- status/precheck/monitor/report
- temel recovery/replan

## Hızlı Başlangıç
```bash
cd ~/graywolf
scripts/graywolf status
scripts/graywolf precheck
scripts/graywolf commands
```

## Temel Komutlar
- `scripts/graywolf status`
- `scripts/graywolf precheck`
- `scripts/graywolf monitor status`
- `scripts/graywolf queue --limit 5`
- `scripts/graywolf approvals`
- `scripts/graywolf report daily`

## Çalışma Akışı
1. `run` ile intent gönder
2. Policy sonucu:
   - `queued` (doğrudan işleme)
   - `confirm_required` (onay bekler)
   - `denied` (yasak intent)
3. `approve/deny` ile karar ver
4. `logs/report` ile sonucu izle

## Kurulum Notu
- Python 3.11+
- Tercihen `.venv` kullan
- Ops komutları için repo kökünden çalış

## Tek Gerçek Teknik Durum Kaynağı
- `docs/PROJECT_CANONICAL_STATE.md`
- `docs/ops/OPERATIONS.md`
- `docs/CLI_COMMANDS.md`
