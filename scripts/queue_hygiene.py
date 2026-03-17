#!/usr/bin/env python3
"""Queue hygiene: separate test artifacts from prod queue/processed."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path('/home/adem/graywolf')
QUEUE = ROOT / 'tasks' / 'queue'
PROCESSED = ROOT / 'tasks' / 'processed'
TEST_QUEUE = ROOT / 'tasks' / 'queue_test'
TEST_PROCESSED = ROOT / 'tasks' / 'processed_test'
REPORT = ROOT / 'reports' / 'queue_hygiene_latest.md'

TEST_SOURCES = {'acceptance-suite', 'api-test', 'telegram-test', 'test', 'qa'}


@dataclass
class MovePlan:
    src: Path
    dst: Path


def _is_test_task(task: dict) -> bool:
    source = str(task.get('source') or '').strip().lower()
    payload = task.get('payload') or {}
    goal = str(task.get('goal') or payload.get('goal') or '').lower()
    task_id = str(task.get('task_id') or '')

    if source in TEST_SOURCES or source.startswith('api-test') or source.startswith('telegram-test'):
        return True

    # acceptance/qa commands produced via command bus
    if task_id.startswith('TASK-CMD-') and source in {'acceptance-suite', 'api-test', 'telegram-test'}:
        return True

    return 'acceptance' in goal


def _collect_plans(src_dir: Path, dst_dir: Path) -> list[MovePlan]:
    plans: list[MovePlan] = []
    if not src_dir.exists():
        return plans
    for p in sorted(src_dir.glob('*.json')):
        try:
            task = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        if _is_test_task(task):
            plans.append(MovePlan(src=p, dst=dst_dir / p.name))
    return plans


def _apply(plans: list[MovePlan]) -> None:
    for plan in plans:
        plan.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(plan.src), str(plan.dst))


def main() -> int:
    ap = argparse.ArgumentParser(description='Graywolf queue hygiene')
    ap.add_argument('--apply', action='store_true', help='Apply moves (default: dry-run report)')
    args = ap.parse_args()

    queue_plans = _collect_plans(QUEUE, TEST_QUEUE)
    processed_plans = _collect_plans(PROCESSED, TEST_PROCESSED)

    if args.apply:
        _apply(queue_plans)
        _apply(processed_plans)

    lines = [
        '# Queue Hygiene Report',
        '',
        f'- mode: {"apply" if args.apply else "dry-run"}',
        f'- queue_test_moves: {len(queue_plans)}',
        f'- processed_test_moves: {len(processed_plans)}',
        '',
        '## queue -> queue_test',
    ]
    lines += [f'- {p.src.name} -> {p.dst}' for p in queue_plans] or ['- none']
    lines += ['', '## processed -> processed_test']
    lines += [f'- {p.src.name} -> {p.dst}' for p in processed_plans] or ['- none']

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(str(REPORT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
