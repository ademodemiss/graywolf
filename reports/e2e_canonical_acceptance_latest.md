# E2E Canonical Acceptance Report

- ts: 2026-03-17T20:32:00.228890
- overall: PASS

## Scenario 1 — command -> task -> report artifact
- status: PASS
- detail: `{"rc": 0, "status": "queued", "task_file": "/home/adem/graywolf/tasks/queue/TASK-CMD-20260317203159-014725.json", "stderr": ""}`

## Scenario 2 — approval required -> callback -> continue
- status: PASS
- detail: `{"request_id": "e678208f-e90f-4caf-9224-f809574b59a8", "final_status": "granted"}`

## Scenario 3 — failure -> recovery -> final result
- status: PASS
- detail: `{"bad_rc": 1, "bad_status": "error", "good_rc": 0, "good_status": "queued", "good_stderr": ""}`
