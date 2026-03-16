import argparse
import json
import time

from infra.incident_response import run_recovery_cycle
from monitor.metrics_collector import collect_metrics


DEFAULT_MOCK_METRICS = {
    'retry_rate': 0.5,
    'dead_letter_rate': 0.15,
    'queue_depth': 60,
    'active_nodes': 1,
}


def run_once(metrics: dict | None = None) -> dict:
    return run_recovery_cycle(metrics or collect_metrics())


def run_loop(interval: int = 60, metrics: dict | None = None):
    try:
        while True:
            result = run_once(metrics)
            print(json.dumps(result, ensure_ascii=False))
            if interval <= 0:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print(json.dumps({'status': 'loop_aborted'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GrayWolf recovery coordinator')
    parser.add_argument('--test-metrics', action='store_true', help='use canned failure metrics')
    parser.add_argument('--loop', type=int, default=0, help='run repeatedly every N seconds (0 = single run)')
    args = parser.parse_args()

    metrics = DEFAULT_MOCK_METRICS if args.test_metrics else None
    run_loop(interval=args.loop, metrics=metrics)
