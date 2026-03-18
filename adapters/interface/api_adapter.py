#!/usr/bin/env python3
from __future__ import annotations

from adapters.interface.audit import write_audit
from adapters.interface.command_schema import validate_envelope
from core.command_bus import CommandBus


def submit_api_command(intent: str, payload: dict, source: str = 'api') -> dict:
    bus = CommandBus('/home/adem/graywolf/tasks/queue', '/home/adem/graywolf/tasks/processed')
    envelope = bus.build_envelope(intent=intent, payload=payload, source=source)

    ok, errs = validate_envelope(envelope)
    if not ok:
        out = {'status': 'error', 'artifacts': {}, 'errors': errs}
        write_audit('api', 'submit', 'error', out)
        return out

    out = bus.submit(envelope)
    write_audit('api', 'submit', out.get('status', 'unknown'), {'command_id': envelope.get('command_id')})
    return out
