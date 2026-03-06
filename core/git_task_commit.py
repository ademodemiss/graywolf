import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from core.task_scope import classify_scope_violations


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        'cmd': ' '.join(cmd),
        'exit_code': p.returncode,
        'stdout': (p.stdout or '').strip(),
        'stderr': (p.stderr or '').strip(),
    }


def _slug(text: str, limit: int = 24) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return (s or 'task')[:limit]


def _branch_exists(name: str) -> bool:
    return _run(['git', 'show-ref', '--verify', f'refs/heads/{name}'])['exit_code'] == 0


def _pick_branch(base_name: str) -> str:
    if not _branch_exists(base_name):
        return base_name
    i = 2
    while True:
        cand = f'{base_name}-{i}'
        if not _branch_exists(cand):
            return cand
        i += 1


def _parse_task(task_path: str) -> dict:
    return json.loads(Path(task_path).read_text(encoding='utf-8'))


def _verify_task(task_path: str) -> dict:
    r = _run(['python3', '-m', 'core.task_runner_v2', '--test', '--task', task_path])
    payload = {}
    if r['stdout']:
        try:
            payload = json.loads(r['stdout'].splitlines()[-1])
        except Exception:
            payload = {'raw': r['stdout']}
    ok = r['exit_code'] == 0 and payload.get('status') == 'ok'
    return {'ok': ok, 'command': r, 'payload': payload}


def _git_status_porcelain() -> tuple[list[str], list[str], list[str]]:
    r = _run(['git', 'status', '--porcelain'])
    staged, unstaged, untracked = [], [], []
    if r['exit_code'] != 0:
        return staged, unstaged, untracked

    for ln in r['stdout'].splitlines():
        if len(ln) < 4:
            continue
        x, y = ln[0], ln[1]
        path = ln[3:]
        if x == '?' and y == '?':
            untracked.append(path)
            continue
        if x != ' ':
            staged.append(path)
        if y != ' ':
            unstaged.append(path)
    return staged, unstaged, untracked


def _staged_files() -> list[str]:
    r = _run(['git', 'diff', '--cached', '--name-only'])
    if r['exit_code'] != 0:
        return []
    return [x for x in r['stdout'].splitlines() if x.strip()]


def run_pipeline(task_path: str, dry_run: bool = False) -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    task = _parse_task(task_path)
    task_id = task.get('id', 'TASK-UNKNOWN')
    title = task.get('title', 'untitled task')
    short_title = title[:72]

    verify = _verify_task(task_path)
    branch_base = f"task/{task_id}-{_slug(short_title)}"
    branch_name = _pick_branch(branch_base)

    staged_before, unstaged_before, untracked_before = _git_status_porcelain()
    scope_eval = classify_scope_violations(task.get('scope', []), staged_before, unstaged_before, untracked_before)

    blocked_files = sorted(set(
        scope_eval['blocked_prestaged'] + scope_eval['blocked_unstaged'] + scope_eval['blocked_untracked']
    ))

    final_status = 'verify_failed_no_commit'
    decision = 'blocked'
    commit_hash = None
    diffstat = ''

    if not verify['ok']:
        final_status = 'verify_failed_no_commit'
        decision = 'blocked'
    elif blocked_files:
        final_status = 'scope_or_dirty_violation_blocked'
        decision = 'blocked'
    else:
        decision = 'allowed'
        if dry_run:
            final_status = 'dry_run_ok'
        else:
            # deterministic branch + collision fallback
            current_branch = _run(['git', 'branch', '--show-current'])
            if current_branch['exit_code'] == 0 and current_branch['stdout'] != branch_name:
                if _branch_exists(branch_name):
                    c = _run(['git', 'checkout', branch_name])
                else:
                    c = _run(['git', 'checkout', '-b', branch_name])
                if c['exit_code'] != 0:
                    final_status = 'branch_checkout_failed'
                    decision = 'blocked'

            if decision == 'allowed':
                scope_files = [str(x) for x in task.get('scope', []) if isinstance(x, str)]
                if scope_files:
                    _run(['git', 'add', '--'] + scope_files)

                staged_after = _staged_files()
                blocked_staged = [x for x in staged_after if x not in scope_files]
                if blocked_staged:
                    final_status = 'staged_scope_violation_blocked'
                    decision = 'blocked'
                    blocked_files = sorted(set(blocked_files + blocked_staged))
                elif not staged_after:
                    final_status = 'no_changes'
                    decision = 'no_commit'
                else:
                    msg = f"{task_id}: {short_title} [evidence:{task_id}]"
                    c = _run(['git', 'commit', '-m', msg])
                    if c['exit_code'] == 0:
                        h = _run(['git', 'rev-parse', '--short', 'HEAD'])
                        commit_hash = h['stdout'] if h['exit_code'] == 0 else None
                        ds = _run(['git', 'diff', '--shortstat', 'HEAD~1', 'HEAD'])
                        diffstat = ds['stdout'] if ds['exit_code'] == 0 else ''
                        final_status = 'committed'
                        decision = 'committed'
                    else:
                        final_status = 'commit_failed'
                        decision = 'blocked'

    finished_at = datetime.now(timezone.utc).isoformat()
    out = {
        'status': 'ok' if final_status in {'dry_run_ok', 'no_changes', 'committed'} else 'failed',
        'task_id': task_id,
        'branch_name': branch_name,
        'commit_hash': commit_hash,
        'staged_files': _staged_files(),
        'blocked_files': blocked_files,
        'diffstat': diffstat,
        'verify_status': 'ok' if verify['ok'] else 'failed',
        'final_status': final_status,
        'decision': decision,
        'started_at': started_at,
        'finished_at': finished_at,
        'dry_run': dry_run,
        'verification_command': verify['command'],
        'scope_evaluation': scope_eval,
    }

    evidence = Path(f'/home/adem/graywolf/reports/task_{task_id}_git_evidence.json')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    out['cert_report_path'] = '/home/adem/graywolf/reports/real_task_certification_v2.json'
    out['report_link'] = str(evidence)
    evidence.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['evidence_path'] = str(evidence)

    # Phase 233 explicit report
    Path('/home/adem/graywolf/reports/task_diff_aware_commit_report.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    return out


def run_test() -> dict:
    nominal = run_pipeline('/home/adem/graywolf/tasks/examples/fix_semantic_search.json', dry_run=True)
    negative = run_pipeline('/home/adem/graywolf/tasks/examples/fix_semantic_search_scope_violation.json', dry_run=False)
    return {
        'status': 'ok' if nominal['status'] == 'ok' and negative['decision'] in {'blocked', 'no_commit'} else 'failed',
        'nominal': {'final_status': nominal['final_status'], 'decision': nominal['decision']},
        'negative': {'final_status': negative['final_status'], 'decision': negative['decision'], 'blocked_files': negative['blocked_files']},
        'artifact': '/home/adem/graywolf/reports/task_diff_aware_commit_report.json',
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--task', default='/home/adem/graywolf/tasks/examples/fix_semantic_search.json')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()

    if a.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    elif a.task:
        print(json.dumps(run_pipeline(a.task, dry_run=a.dry_run), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle'}, ensure_ascii=False))
