#!/usr/bin/env python3
"""Generate a lightweight repository inventory report.

Output: reports/repo_inventory.json
"""

from __future__ import annotations

import collections
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "repo_inventory.json"


def _run(cmd: str) -> list[str]:
    data = subprocess.check_output(["bash", "-lc", cmd], cwd=ROOT, text=True)
    return [line for line in data.splitlines() if line.strip()]


def main() -> int:
    tracked = _run("git ls-files")
    status = _run("git status --porcelain")

    modified: list[str] = []
    untracked: list[str] = []
    for line in status:
        if line.startswith("?? "):
            untracked.append(line[3:])
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        modified.append(path)

    roots: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: {"tracked": 0, "modified": 0, "untracked": 0}
    )

    for p in tracked:
        root = p.split("/", 1)[0] if "/" in p else "."
        roots[root]["tracked"] += 1
    for p in modified:
        root = p.split("/", 1)[0] if "/" in p else "."
        roots[root]["modified"] += 1
    for p in untracked:
        root = p.split("/", 1)[0] if "/" in p else "."
        roots[root]["untracked"] += 1

    out = {
        "totals": {
            "tracked": len(tracked),
            "modified": len(modified),
            "untracked": len(untracked),
        },
        "roots": dict(
            sorted(roots.items(), key=lambda kv: (-(kv[1]["modified"] + kv[1]["untracked"]), kv[0]))
        ),
        "high_churn_roots": [
            root for root, d in roots.items() if d["modified"] + d["untracked"] >= 10
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(json.dumps(out["totals"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
