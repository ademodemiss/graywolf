# E2E Canonical Acceptance Report

- ts: 2026-03-18T23:26:42.046304
- overall: PASS

## Scenario 1 — command -> task -> report artifact
- status: PASS
- detail: `{"rc": 0, "status": "queued", "task_file": "/home/adem/graywolf/tasks/queue/TASK-CMD-20260318232641-8e6887.json", "stderr": ""}`

## Scenario 2 — approval required -> callback -> continue
- status: PASS
- detail: `{"request_id": "929a3ca7-5ac6-49ae-ab6c-7d479b373b68", "final_status": "granted"}`

## Scenario 3 — failure -> recovery -> final result
- status: PASS
- detail: `{"bad_rc": 1, "bad_status": "error", "good_rc": 0, "good_status": "queued", "good_stderr": ""}`
