# GRAYWOLF_CANONICAL_STATE

Last updated: 2026-03-23

## Product identity
- Product: Graywolf
- Goal: OpenClaw davranış paritesine yakın değil, **eşdeğer assistant deneyimi**
- Runtime dependency policy: OpenClaw runtime bağımlılığı **yok** (graft/adaptation only)

## Canonical core (protected)
1. CLI / entrypoints
   - `scripts/graywolf`
   - `core/graywolf_cli.py`
2. Assistant layer
   - `core/graywolf_cli.py`
   - `core/assistant_context.py`
   - `core/assistant_explainer.py`
3. Agent loop
   - `agent/simple_agent_loop.py`
4. Approval / resume / continuity
   - `core/approval.py`
   - `monitor/approval_callback_router.py`
   - `sessions/*`
5. Runtime / tasks / state
   - `core/runtime.py`
   - `core/command_bus.py`
   - `core/task_queue.py`
   - `scripts/run_autonomy_worker.py`
6. Channel bridge
   - `telegram_bot.py`
7. Quality gates
   - `tests/*`
   - `scripts/release_precheck.sh`

## OpenClaw graft status
- Attribution/Licensing: active (`docs/OPENCLAW_ATTRIBUTION.md`, `licenses/OPENCLAW_LICENSE_MIT.txt`)
- Source mapping: active (`docs/OPENCLAW_SOURCE_MAP.md`)
- Phase status: 0..6 completed, 7 canonicalized

## Acceptance baseline
- Regression pack: PASS
- Canonical E2E: PASS
- Release precheck: PASS

## Change policy (post phase-7)
- Runtime spine changes require explicit approval.
- Assistant/channel/tooling improvements must preserve tests + precheck + E2E.
- OpenClaw-derived changes must keep attribution/source-map updated.
