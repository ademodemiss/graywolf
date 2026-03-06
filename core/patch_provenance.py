import argparse
import json
import subprocess
from pathlib import Path

REPORT = Path('/home/adem/graywolf/reports/patch_provenance_report.json')


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {'cmd': ' '.join(cmd), 'exit_code': p.returncode, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def run_test():
    ev = Path('/home/adem/graywolf/reports/task_TASK-001_git_evidence.json')
    evidence = {}
    if ev.exists():
        try:
            evidence = json.loads(ev.read_text(encoding='utf-8'))
        except Exception:
            evidence = {}

    changed_files = evidence.get('staged_files', []) or evidence.get('changed_files', []) or []
    commit_hash = evidence.get('commit_hash')

    diffstat_r = _run(['git', 'diff', '--shortstat'])

    out = {
        'status': 'ok',
        'task_id': evidence.get('task_id', 'TASK-001'),
        'commit_hash': commit_hash,
        'changed_files': changed_files,
        'diffstat': diffstat_r.get('stdout', ''),
        'evidence_link': str(ev),
        'has_evidence': ev.exists(),
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
