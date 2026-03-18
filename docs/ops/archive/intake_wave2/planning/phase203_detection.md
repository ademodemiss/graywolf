# Phase 203/02 — Detection ve Event Tespiti

Bu belge, Faz 203'ün detection aşamasında yapılan değişiklikleri ve otomatik trigger mekanizmasını belgeliyor.

## Yeni veya güncellenen bileşenler
- `monitor/metrics_collector.py` artık `failure_rate`, `dead_letter_count`, `unhappy_tasks`, `attempt_rate`, `running_tasks` ve `failed_tasks` gibi hata/spike göstergelerini hesaplıyor. Bu metrikler, alert mekanizmalarının kriterlerini zenginleştiriyor.
- `monitor/recovery_dispatcher.py` EventBus üzerinden `EventTypes.TASK_FAILED` ve `EventTypes.NODE_DEAD` olaylarını dinliyor. Her tetikli olayda `collect_metrics` + `run_recovery_cycle` çağrılıyor; sonuçlar `logs/recovery_dispatcher.log`'a yazılıyor ve ileride alert/telemetry katmanlarına besleniyor.
- `tests/test_recovery_dispatcher.py` dispatcher'ın sonraki koşullarda recovery çağırdığını ve cooldown haliyle atladığını doğruluyor (2/2 test, yeni `mock` log). Bu, detection logic'inin behema halini test ediyor.

## How to exercise
1. `python3 -m monitor.recovery_dispatcher --cooldown 60` (veya `--cooldown 0` hızlı tetik için) çalıştırarak event-driven dispatcher'ı dinlemede tut.
2. EventBus'a `EventTypes.TASK_FAILED` publish eden komutları çalıştır (örn. `jobqueue.job_scheduler` içinden `BUS.publish(EventTypes.TASK_FAILED, {...})`) ve `logs/recovery_dispatcher.log` içinde kayıtları takip et.
3. Bu modül phase 203 detection tamamlandıktan sonra sürekli olarak agent_loop veya orchestrator içinde başlatılmalı.
