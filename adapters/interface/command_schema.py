from __future__ import annotations


def validate_envelope(envelope: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = ['command_id', 'intent', 'payload', 'source']
    for key in required:
        if key not in envelope:
            errors.append(f'missing:{key}')

    if 'intent' in envelope and not str(envelope.get('intent') or '').strip():
        errors.append('invalid:intent_empty')
    if 'payload' in envelope and not isinstance(envelope.get('payload'), dict):
        errors.append('invalid:payload_not_object')

    return (len(errors) == 0, errors)
