# Intent Policy (Runtime Command Bus)

Graywolf command bus artık intent bazlı policy gate uygular.

## Decisions
- `ALLOW` -> task queue'ya alınır (`status=queued`)
- `CONFIRM` -> kuyruğa alınmaz, onay beklenir (`status=confirm_required`)
- `DENY` -> reddedilir (`status=denied`)

## Default examples
- ALLOW: `healthcheck`, `risk_summary`, `repo_status`, `chat_command`, `status`
- CONFIRM: `deploy`, `delete_artifact`, `financial_trade`, `system_change`, `shutdown_service`
- DENY: `system_reboot`, `wipe_data`, `disable_guardrails`

## Files
- `policies/intent_policy.py`
- `core/command_bus.py`
- `core/runtime.py`

## Approval callback flow
`confirm_required` dönen komutlar pending approval store'a yazılır (`sessions/pending_approvals.json`).

Grant callback örneği:
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m core.runtime approval-callback --callback-data 'approval.grant:APR-...'
```

Bu çağrı onayı işler ve ilgili pending komutu queue'ya alır.

## Quick test
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m core.runtime submit-command --intent deploy --payload '{"goal":"prod deploy"}'
```
