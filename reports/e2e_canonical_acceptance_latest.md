# E2E Canonical Acceptance Report

- ts: 2026-03-17T20:26:47.523639
- overall: PASS

## Scenario 1 — command -> task -> report artifact
- status: PASS
- detail: `{"rc": 0, "status": "queued", "task_file": "/home/adem/graywolf/tasks/queue/TASK-CMD-20260317202647-1736b5.json", "stderr": ""}`

## Scenario 2 — approval required -> callback -> continue
- status: PASS
- detail: `{"request_id": "0809d3b1-263f-4df3-8270-228bd000ed02", "final_status": "granted"}`

## Scenario 3 — failure -> recovery -> final result
- status: PASS
- detail: `{"bad_rc": 1, "bad_status": "error", "good_rc": 0, "good_status": "queued", "good_stderr": ""}`
