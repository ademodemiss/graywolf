# Graywolf CLI Commands (V1.0)

## Core
- `graywolf status` → runtime/daemon/queue/approval özeti
- `graywolf precheck` → release gate
- `graywolf doctor` → precheck alias
- `graywolf monitor start|stop|status` → daemon kontrol
- `graywolf queue [--limit N]` → queue/processed özeti
- `graywolf approvals` → pending/granted/denied özeti

## Execution
- `graywolf run --intent <intent> [--goal "..."] [--payload '{...}']`
- `graywolf approve <request_id>`
- `graywolf deny <request_id>`

## Observability
- `graywolf logs --target daemon|terminal|precheck [--lines N]`
- `graywolf report daily|weekly`

## Help
- `graywolf commands`
- `graywolf help [komut]`

## Quick
```bash
scripts/graywolf status
scripts/graywolf precheck
scripts/graywolf run --intent healthcheck --goal "smoke"
scripts/graywolf approvals
scripts/graywolf queue --limit 5
scripts/graywolf report daily
```
