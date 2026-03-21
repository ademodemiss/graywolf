#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.autonomy_summary_tool import build_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Status reporter")
    parser.add_argument("mode", nargs="?", default=None)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--points", type=int, default=8)
    parser.add_argument("--summary-points", type=int, default=None)
    parser.add_argument("--bullet-points", type=int, default=None)
    parser.add_argument("--format", default=None)
    parser.add_argument("--output-file", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    points = args.points
    if args.summary_points is not None:
        points = args.summary_points
    if args.bullet_points is not None:
        points = args.bullet_points
    text = build_summary(points)

    out_target = args.output_file or args.output
    if out_target:
        import os
        out = out_target
        if not out.startswith("/"):
            out = f"/home/adem/graywolf/{out}"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"written:{out}")
        return 0

    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
