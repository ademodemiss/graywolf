# Release Hardening Checklist (Final Phase)

## A) Runtime Stability
- [x] `scripts/daily_healthcheck.sh` passes
- [x] `scripts/operator_tasks.sh all` passes
- [x] `scripts/run_three_real_tasks.sh` returns 3/3 completed
- [x] Autonomy daemon runs idle/work cycles without crash

## B) Safety & Guardrails
- [x] Shell policy safe-write allowlist active (`logs/`, `reports/`, `tasks/`)
- [x] High-risk command quality filter active in orchestrator
- [x] Unknown tool-script mapping fallback to `tools/status_reporter.py`

## C) LLM Routing
- [x] Router handles both string and tuple adapter outputs
- [x] Fallback logging present for diagnosis
- [x] Deprecated Gemini fallback made opt-in (`GRAYWOLF_ALLOW_LEGACY_GEMINI=1`)

## D) Ops UX
- [x] Single-command operator script exists
- [x] Real-task summary report exists
- [x] Risk summary script exists

## E) Remaining (post-release improvements)
- [x] Fine-grained task success scoring (v1: per-task quality_score + average score in `logs/three_tasks_summary.md`)
- [x] Financial decision support hardening (data validation + quality/meta checks in `financial_data_tool`)
- [x] Extended self-improve regression suite (`scripts/self_improve_regression.sh`)
