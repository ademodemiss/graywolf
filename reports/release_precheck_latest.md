# Release Precheck Report
- ts: 2026-03-17T20:31:57+03:00

## Deprecation Guard
- cmd: `/home/adem/graywolf/scripts/deprecation_guard.sh`
- status: PASS
```
[OK] No deprecated runtime references in active code paths.
```

## Operator Tasks (all)
- cmd: `/home/adem/graywolf/scripts/operator_tasks.sh all`
- status: PASS
```
repo:ok
health:ok
risk:ok
done:all
```

## E2E Canonical Acceptance
- cmd: `PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/scripts/e2e_canonical_acceptance.py`
- status: PASS
```
/home/adem/graywolf/reports/e2e_canonical_acceptance_latest.md
```

