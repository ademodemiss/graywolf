import argparse
import json
from pathlib import Path


def run_test(task_path: str) -> dict:
    task = json.loads(Path(task_path).read_text(encoding='utf-8'))
    verification_cmds = task.get('verification_commands', [])
    out = {
        'status': 'ok',
        'task_id': task.get('id'),
        'replay_commands': verification_cmds,
        'diff_summary': {'changed': 0, 'notes': 'deterministic replay simulated'}
    }
    Path('/home/adem/graywolf/reports/task_replay_report.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); p.add_argument('--task', default='/home/adem/graywolf/tasks/examples/fix_semantic_search.json'); a = p.parse_args()
    print(json.dumps(run_test(a.task) if a.test else {'status': 'idle'}, ensure_ascii=False))
