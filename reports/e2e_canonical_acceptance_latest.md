# E2E Canonical Acceptance Report

- ts: 2026-03-23T21:02:56.553301
- overall: PASS

## Scenario 1 — command -> task -> report artifact
- status: PASS
- detail: `{"rc": 0, "status": "queued", "task_file": "/home/adem/graywolf/tasks/queue/TASK-CMD-20260323210256-fa38b0.json", "stderr": ""}`

## Scenario 2 — approval required -> callback -> continue
- status: PASS
- detail: `{"request_id": "96eee421-ee20-4265-9a68-b505b1b5fe75", "final_status": "granted"}`

## Scenario 3 — failure -> recovery -> final result
- status: PASS
- detail: `{"bad_rc": 1, "bad_status": "error", "good_rc": 0, "good_status": "queued", "good_stderr": ""}`
