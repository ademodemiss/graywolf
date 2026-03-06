import argparse
import json
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {'cmd': ' '.join(cmd), 'exit_code': p.returncode, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def run_test() -> dict:
    branch = _run(['git', 'branch', '--show-current'])
    status = _run(['git', 'status', '--short'])
    evidence = Path('/home/adem/graywolf/reports/task_TASK-001_evidence.json').exists()
    out = {
        'status': 'ok',
        'branch': branch.get('stdout', ''),
        'status_short': status.get('stdout', ''),
        'evidence_exists': evidence,
        'commit_message_template': 'feat(task): TASK-001 semantic_search verified [evidence: reports/task_TASK-001_evidence.json]'
    }
    Path('/home/adem/graywolf/reports/task_commit_mode_report.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
