# E2E Canonical Acceptance Report

- ts: 2026-03-18T23:08:54.582308
- overall: PASS

## Scenario 1 — command -> task -> report artifact
- status: PASS
- detail: `{"rc": 0, "status": "queued", "task_file": "/home/adem/graywolf/tasks/queue/TASK-CMD-20260318230854-048c4c.json", "stderr": ""}`

## Scenario 2 — approval required -> callback -> continue
- status: PASS
- detail: `{"request_id": "8cf1c191-0144-4505-9b17-dad5b24f3f8b", "final_status": "granted"}`

## Scenario 3 — failure -> recovery -> final result
- status: PASS
- detail: `{"bad_rc": 1, "bad_status": "error", "good_rc": 0, "good_status": "queued", "good_stderr": ""}`
