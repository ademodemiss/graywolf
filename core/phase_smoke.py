import argparse
import importlib
import json
from datetime import datetime, timezone

PHASE_IMPORTS = {
    13: ["self_improve"],
    14: ["monitor", "monitor.system_metrics"],
    15: ["infrastructure", "infrastructure.infra_monitor", "infrastructure.auto_scaler"],
    16: ["policies.shell_policy", "tools.terminal_tool", "core.event_bus"],
    17: ["plugins.plugin_loader", "agents", "events"],
    18: ["dashboard"],
    19: ["policies.shell_policy", "core.agent_loop"],
    20: ["core.agent_loop"],
}


def run_phase_smoke(phase: int) -> dict:
    mods = PHASE_IMPORTS.get(phase, [])
    ok = True
    imported = []
    errors = []
    for m in mods:
        try:
            importlib.import_module(m)
            imported.append(m)
        except Exception as e:
            ok = False
            errors.append({"module": m, "error": repr(e)})
    return {
        "status": "ok" if ok else "failed",
        "phase": phase,
        "imported": imported,
        "errors": errors,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", type=int, required=True)
    p.add_argument("--test", action="store_true")
    args, unknown = p.parse_known_args()
    if unknown:
        print(json.dumps({"status": "error", "error": "unknown_args", "unknown": unknown}, ensure_ascii=False))
        raise SystemExit(2)
    if not args.test:
        print(json.dumps({"status": "idle"}, ensure_ascii=False))
        return
    out = run_phase_smoke(args.phase)
    print(json.dumps(out, ensure_ascii=False))
    raise SystemExit(0 if out["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
