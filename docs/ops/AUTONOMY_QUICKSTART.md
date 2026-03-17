# Autonomy Quickstart (Safe)

## 1) Tek seferlik kısa görev döngüsü
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m core.full_autonomy
```

## 2) Çok adımlı controller smoke
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m core.full_autonomy_controller
```

## 3) Güvenli günlük sağlık kontrolü
```bash
/home/adem/graywolf/scripts/daily_healthcheck.sh
```

## Not
- LLM hazır değilse task'lar patlamak yerine `blocked` olarak işaretlenir.
- Önce healthcheck, sonra autonomy komutlarını çalıştır.
