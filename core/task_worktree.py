import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/adem/graywolf')
TMP = ROOT / 'tmp' / 'worktree_task'
REPORT = ROOT / 'reports' / 'task_worktree_execution_report.json'


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {'cmd': ' '.join(cmd), 'exit_code': p.returncode, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def run_test():
    TMP.parent.mkdir(parents=True, exist_ok=True)
    if TMP.exists():
        shutil.rmtree(TMP)

    copy_r = _run(['cp', '-a', str(ROOT / 'coding'), str(TMP)])

    cand1 = TMP / 'coding' / 'semantic_search.py'
    cand2 = TMP / 'semantic_search.py'
    target = cand1 if cand1.exists() else cand2
    check_r = _run(['python3', '-m', 'py_compile', str(target)])

    cleaned = False
    if TMP.exists():
        shutil.rmtree(TMP)
        cleaned = not TMP.exists()

    out = {
        'status': 'ok' if copy_r['exit_code'] == 0 and check_r['exit_code'] == 0 and cleaned else 'failed',
        'worktree_path': str(TMP),
        'copy': copy_r,
        'verify': check_r,
        'cleanup_ok': cleaned,
        'main_repo_touched': False,
        'ts': datetime.now(timezone.utc).isoformat(),
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
