# Operations Hub (Single-Page)

Bu dosya günlük operasyon için tek sayfa referanstır.

## Release Öncesi Zorunlu Gate
```bash
/home/adem/graywolf/scripts/release_precheck.sh
```

Bu komut sırasıyla şunları koşar ve herhangi biri fail olursa release'i durdurur:
1. `scripts/deprecation_guard.sh`
2. `scripts/operator_tasks.sh all`
3. `scripts/e2e_canonical_acceptance.py`

Rapor: `reports/release_precheck_latest.md`

## Queue Hijyeni (test/prod ayrımı)
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/scripts/queue_hygiene.py --apply
```
- Test/acceptance görevlerini `tasks/processed_test` / `tasks/queue_test` altına ayırır.
- Rapor: `reports/queue_hygiene_latest.md`

## Günlük Sağlık Kontrolü
1. Dashboard test:
```bash
python3 /home/adem/graywolf/dashboard/server.py --test
```
2. Replan health:
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/monitor/replan_health_reporter.py --telegram
```
3. Trend dry-run:
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/monitor/learning_recovery_trend.py --dry-run
```

## Kritik Zincir (Sıralı)
1. `replan_health_reporter.py`
2. `replan_learning_reporter.py`
3. `replan_learning_autopilot.py`
4. `learning_reliability_trends.py`
5. `learning_recovery_coordinator.py`
6. `learning_recovery_inspector.py`
7. `learning_recovery_trend.py`

## Notlar
- Cronlar kontrollü açılmalı (önce 1-2 job, sonra kademeli).
- Şüpheli/çok büyük duration değerleri trend monitor tarafında normalize edilir.
- Telegram konfig yoksa scriptler `TELEGRAM_NOT_CONFIGURED` ile güvenli şekilde skip eder.

## Kanonik Durum Dosyaları
- Repo haritası: `docs/REPO_MAP.md`
- Toparlama planı: `REPO_CLEANUP_PLAN.md`
- Envanter raporu: `reports/repo_inventory.json`
