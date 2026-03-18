# Autonomy Quickstart (Canonical)

## 1) Tek seferlik worker çalıştırma
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/scripts/run_autonomy_worker.py
```

## 2) Daemon durum kontrolü
```bash
/home/adem/graywolf/scripts/autonomy_daemon.sh status
```

## 3) Daemon başlat/durdur
```bash
/home/adem/graywolf/scripts/autonomy_daemon.sh start
/home/adem/graywolf/scripts/autonomy_daemon.sh stop
```

## 4) Güvenli günlük sağlık kontrolü
```bash
/home/adem/graywolf/scripts/daily_healthcheck.sh
```

## Not
- Canonical runtime hattı: `core/autonomous_loop.py` + `scripts/run_autonomy_worker.py` + `scripts/autonomy_daemon.sh`
- `core.full_autonomy*` dosyaları legacy/deprecate kabul edilir.
