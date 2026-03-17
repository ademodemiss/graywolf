#!/usr/bin/env python3
from __future__ import annotations

import json

from adapters.interface.audit import write_audit
from adapters.interface.command_schema import validate_envelope
from core.command_bus import CommandBus


def submit_telegram_message(text: str, source: str = 'telegram') -> dict:
    bus = CommandBus('/home/adem/graywolf/tasks/queue', '/home/adem/graywolf/tasks/processed')
    envelope = bus.build_envelope(intent='chat_command', payload={'text': text, 'goal': text}, source=source)

    ok, errs = validate_envelope(envelope)
    if not ok:
        out = {'status': 'error', 'artifacts': {}, 'errors': errs}
        write_audit('telegram', 'submit', 'error', out)
        return out

    out = bus.submit(envelope)
    write_audit('telegram', 'submit', out.get('status', 'unknown'), {'command_id': envelope.get('command_id')})
    return out


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description='Graywolf Telegram Interface Adapter')
    p.add_argument('--text', default='healthcheck çalıştır')
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        print(json.dumps(submit_telegram_message(args.text), ensure_ascii=False))


if __name__ == '__main__':
    main()
