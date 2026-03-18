# NO_BREAK_CLEANUP_PLAN (draft)

- ts: 2026-03-18T21:11:20+03:00
- policy: no-break (davranış değiştirmeden)

## Inventory Summary
- tracked_modified: 14
- untracked: 103

## Wave 1 (safe, no runtime impact)

### keep (candidate)
- docs/**
- planning/**
- reports/** (except obviously bad fixtures)
- tests/**
- verification/**

### archive (candidate)
- tools/discovery_engine.md
- tools/discovery_engine_analysis.md
- tools/discovery_engine_improvement.md
- reports/bad_code.py
- phase204/** (if historical notes only)

### drop-candidate (needs explicit review before delete)
- duplicate markdown notes in core/: autonomous_loop.md / autonomous_loop_enhancements.md
- stale generated artifacts under tasks/processed* and reports/dashboard/evidence if duplicated elsewhere

## Wave 2 (tracked modified handling)
1. Runtime-independent docs/report changes -> separate commit
2. Runtime/code touched files -> only if tests + precheck green
3. Keep .env local-only (never commit secrets)

## Guardrails
- No rm; only move-to-archive or keep
- release_precheck must stay PASS
- CI release-precheck must stay green
