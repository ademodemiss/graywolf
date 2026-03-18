# Night Monitoring Starter

## Amaç
Gece boyunca minimum müdahaleyle stabiliteyi izlemek.

## Başlatma (manuel)
1. Precheck:
```bash
/home/adem/graywolf/scripts/release_precheck.sh
```
2. Daily ops turu:
```bash
/home/adem/graywolf/scripts/ops_automation.sh daily
```
3. Runtime snapshot:
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m core.runtime status --session-id night-monitor
```

## Gece kontrol aralığı
- Öneri: 2-3 saatte bir
- Kontrol metrikleri:
  - daemon running mi?
  - queue depth anormal artıyor mu?
  - pending approvals birikiyor mu?

## Alarm koşulları
- `release_precheck` FAIL
- daemon stopped/crash
- queue depth sürekli artıyor ve düşmüyor
- approval pending uzun süre kapanmıyor

## Hızlı müdahale
```bash
/home/adem/graywolf/scripts/autonomy_daemon.sh stop
/home/adem/graywolf/scripts/autonomy_daemon.sh start
/home/adem/graywolf/scripts/operator_tasks.sh all
```
