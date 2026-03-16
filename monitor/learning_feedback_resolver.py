import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")


def _read_entries(path: Path | str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    entries: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _print_entry(entry: dict, detail: bool = False) -> None:
    print("--- Learning Feedback ---")
    print(f"request_id: {entry.get('request_id')}")
    print(f"workflow: {entry.get('workflow')}")
    print(f"status: {entry.get('learning_status')} | category: {entry.get('learning_feedback_category')}")
    print(f"reliability_score: {entry.get('learning_reliability_score')} | feedback: {entry.get('learning_feedback')}")
    print(f"duration_ms: {entry.get('learning_duration_ms')} | follow-up: {entry.get('learning_follow_up_notes')}")
    if detail:
        print("full entry:")
        print(json.dumps(entry, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Learning feedback resolver")
    parser.add_argument("--log", default=LEARNING_LOG, help="Learning log yolu")
    parser.add_argument("--last", action="store_true", help="Son entry’i göster")
    parser.add_argument("--count", type=int, default=1, help="Son kaç entry gösterilsin")
    parser.add_argument("--detail", action="store_true", help="Detaylı gösterim")
    args = parser.parse_args()

    entries = _read_entries(args.log)
    if not entries:
        print("Öğrenme girdisi bulunamadı.")
        return

    selected = entries[-args.count :] if args.count else entries
    for entry in selected:
        _print_entry(entry, detail=args.detail)
        if not args.count or args.count == 1:
            break


if __name__ == "__main__":
    main()
