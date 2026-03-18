# Ops Automation

## Script
- `scripts/ops_automation.sh`

## Modes
- `daily`: operator tasks + queue hygiene
- `prerelease`: release precheck gate
- `all`: daily + prerelease

## Commands
```bash
/home/adem/graywolf/scripts/ops_automation.sh daily
/home/adem/graywolf/scripts/ops_automation.sh prerelease
/home/adem/graywolf/scripts/ops_automation.sh all
```

## Suggested cron
```cron
# Daily maintenance (every day 09:00)
0 9 * * * /home/adem/graywolf/scripts/ops_automation.sh daily >> /home/adem/graywolf/logs/ops_automation.log 2>&1

# Pre-release gate reminder (manual trigger preferred)
# /home/adem/graywolf/scripts/ops_automation.sh prerelease
```
