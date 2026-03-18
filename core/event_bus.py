import argparse
import datetime
import json
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
EVENT_LOG = ROOT / 'events' / 'events.log'


class EventBus:
    def __init__(self):
        self.subscribers: dict[str, list[Callable[[dict], None]]] = {}
        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)

    def subscribe(self, event_type: str, handler: Callable[[dict], None]):
        self.subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, payload: dict):
        event = {
            'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'type': event_type,
            'payload': payload,
        }
        with open(EVENT_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')

        for handler in self.subscribers.get(event_type, []):
            handler(event)
        for handler in self.subscribers.get('*', []):
            handler(event)


def _line_count() -> int:
    if not EVENT_LOG.exists():
        return 0
    return len(EVENT_LOG.read_text(encoding='utf-8').splitlines())


def run_test() -> dict:
    from core.event_types import EventTypes

    bus = EventBus()
    consumed = []

    def consume(evt: dict):
        consumed.append(evt['type'])

    bus.subscribe('*', consume)

    before = _line_count()
    bus.publish(EventTypes.TASK_CREATED, {'task_id': 't1'})
    bus.publish(EventTypes.TASK_STARTED, {'task_id': 't1'})
    bus.publish(EventTypes.TASK_COMPLETED, {'task_id': 't1'})
    bus.publish(EventTypes.NODE_HEARTBEAT, {'node_id': 'n1'})
    bus.publish(EventTypes.WORKFLOW_COMPLETED, {'workflow_id': 'w1'})
    after = _line_count()

    return {
        'status': 'ok',
        'published': 5,
        'consumed_count': len(consumed),
        'consumed_sample': consumed[:5],
        'log_lines_before': before,
        'log_lines_after': after,
        'log_grew': after > before,
    }


def main():
    p = argparse.ArgumentParser(description='GrayWolf Event Bus')
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
        return

    print(json.dumps({'status': 'idle'}, ensure_ascii=False))


BUS = EventBus()


if __name__ == '__main__':
    main()
