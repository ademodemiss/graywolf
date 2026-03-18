# Graywolf Operations (V1.0)

Bu dosya günlük operasyon için tek sayfa runbook'tur.

## 1) Günlük Hızlı Kontrol
```bash
scripts/graywolf status
scripts/graywolf precheck
scripts/graywolf monitor status
```

## 2) Komut Çalıştırma
```bash
scripts/graywolf run --intent healthcheck --goal "günlük sağlık kontrolü"
```

## 3) Approval Akışı
- Pending liste:
```bash
scripts/graywolf approvals
```
- Onay ver:
```bash
scripts/graywolf approve <request_id>
```
- Reddet:
```bash
scripts/graywolf deny <request_id>
```

## 4) Queue / Log / Report
```bash
scripts/graywolf queue --limit 10
scripts/graywolf logs --target daemon --lines 50
scripts/graywolf report daily
```

## 5) Release Gate (zorunlu)
```bash
scripts/graywolf precheck
```
Rapor: `reports/release_precheck_latest.md`

## 6) Incident Mini-Protokol
1. `status` + `monitor status`
2. `logs --target daemon`
3. gerekirse `monitor stop` -> `monitor start`
4. `precheck`
5. `report daily`

## 7) Operasyon Kuralları
- Runtime/state artefaktlarını commit etme (`sessions/*`, `tasks/queue*`, rolling reports)
- Riskli intentlerde approval beklemeden işleme geçme
- Her düzeltme turunda precheck çalıştır
