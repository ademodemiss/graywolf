import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from cluster.node_manager import BUS as NODE_BUS
from core.event_types import EventTypes
from infra.incident_response import run_recovery_cycle
from jobqueue.job_scheduler import BUS as SCHED_BUS
from jobqueue.task_queue import BUS as TASK_BUS
from monitor.metrics_collector import collect_metrics

RECOVERY_LOG = Path('/home/adem/graywolf/logs/recovery_dispatcher.log')


class RecoveryDispatcher:
    def __init__(self, buses: Iterable[object] | None = None, cooldown_seconds: int = 60):
        self.cooldown = cooldown_seconds
        self._last_run_ts = 0.0
        self.buses = list(buses or {TASK_BUS, SCHED_BUS, NODE_BUS})
        self._subscribe()

    def _subscribe(self):
        for bus in self.buses:
            bus.subscribe(EventTypes.TASK_FAILED, self._on_task_failed)
            bus.subscribe(EventTypes.NODE_DEAD, self._on_node_dead)

    def _on_task_failed(self, event: dict):
        self._handle_event('task_failed', event)

    def _on_node_dead(self, event: dict):
        self._handle_event('node_dead', event)

    def _handle_event(self, source: str, event: dict):
        now_ts = time.monotonic()
        if self.cooldown and now_ts - self._last_run_ts < self.cooldown:
            self._record_summary({
                'status': 'skipped',
                'reason': 'cooldown',
                'source': source,
                'event': event,
                'ts': datetime.now(timezone.utc).isoformat(),
            })
            return

        self._last_run_ts = now_ts
        metrics = collect_metrics()
        result = run_recovery_cycle(metrics)
        summary = {
            'status': 'recovery_run',
            'source': source,
            'event': event,
            'metrics_snapshot': metrics,
            'result': result,
            'ts': datetime.now(timezone.utc).isoformat(),
        }
        self._record_summary(summary)

    def _record_summary(self, payload: dict):
        RECOVERY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(RECOVERY_LOG, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + '\n')

    def run(self):
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print('recovery dispatcher stopped')


def main():
    parser = argparse.ArgumentParser(description='GrayWolf recovery dispatcher (event-driven)')
    parser.add_argument('--cooldown', type=int, default=60, help='minimum seconds between consecutive recovery calls')
    args = parser.parse_args()

    dispatcher = RecoveryDispatcher(cooldown_seconds=args.cooldown)
    print('recovery dispatcher is listening for task/node events...')
    dispatcher.run()


if __name__ == '__main__':
    main()
