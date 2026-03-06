import argparse
import json
from pathlib import Path


def run_test() -> dict:
    task = Path('/home/adem/graywolf/tasks/examples/fix_semantic_search.json').exists()
    ev1 = Path('/home/adem/graywolf/reports/task_TASK-001_evidence.json').exists()
    ev2 = Path('/home/adem/graywolf/reports/task_runner_v2_report.json').exists()
    ev3 = Path('/home/adem/graywolf/reports/git_task_commit_report.json').exists()
    certified = task and ev1 and ev2 and ev3
    out = {
        'status': 'ok' if certified else 'failed',
        'task_file': task,
        'evidence': {'task_runner_v1': ev1, 'task_runner_v2': ev2, 'git_report': ev3},
        'certified': certified,
    }
    Path('/home/adem/graywolf/reports/real_task_certification_v2.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
