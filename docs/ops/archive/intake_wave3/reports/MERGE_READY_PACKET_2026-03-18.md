# Merge Ready Packet — 2026-03-18

## Status
Branch: `task/TASK-252-orchestrator-sleep-refactor`
Durum: **MERGE READY**

## Validation Snapshot
- `scripts/release_precheck.sh` => PASS
- `tests/test_v2_runtime_foundation.py` => 6 passed
- `core.runtime status` => daemon running, queue_depth=0, pending approvals=0

## Key Commits
- `c5e1c90` chore(v2): freeze foundation and add release/queue operations gates
- `b7d2f91` feat(v2.1): add CI precheck gate, runtime tests, and ops automation
- `d4ecd88` feat(policy): add intent approval gate and API callback-to-queue flow
- `d30b0e1` docs(ops): add operator playbook, merge checklist, and night monitoring starter
- `0756636` fix(runtime): count only truly pending command approvals in status

## Merge Notes
- Runtime state file `sessions/pending_approvals.json` **commitlenmemeli**.
- OpenClaw sadece referans; mimari Graywolf-first.

## Suggested merge flow (auth olan ortamda)
```bash
git checkout main
git pull --rebase origin main
git merge --no-ff task/TASK-252-orchestrator-sleep-refactor -m "merge: graywolf v2 foundation + hardening"
git push origin main
```
