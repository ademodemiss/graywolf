import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path('/home/adem/graywolf')
LOG_FILE = BASE_DIR / 'logs' / 'plan_validator.log'
SUMMARY_LOG = BASE_DIR / 'logs' / 'learning_recovery_summary.log'
FORBIDDEN_SNIPPETS = ['rm -rf', 'sudo']


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_log(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')


def validate_workflow(path: Path) -> tuple[bool, list[str], dict]:
    errors = []
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return False, [f'JSON decode failed: {exc}'], {}

    if 'name' not in payload:
        errors.append('missing workflow name')
    steps = payload.get('steps')
    if not steps or not isinstance(steps, list):
        errors.append('missing steps list')
        return False, errors, payload

    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f'step #{idx} is not an object')
            continue
        if 'name' not in step:
            errors.append(f'step #{idx} missing name')
        if 'cmd' not in step:
            errors.append(f'step #{idx} missing cmd')
        else:
            for snippet in FORBIDDEN_SNIPPETS:
                if snippet in step['cmd']:
                    errors.append(f'step #{idx} contains forbidden snippet {snippet}')
    return len(errors) == 0, errors, payload


def run_workflow(path: Path, execute: bool) -> dict:
    valid, issues, payload = validate_workflow(path)
    try:
        rel_path = str(path.relative_to(BASE_DIR))
    except ValueError:
        rel_path = str(path)
    summary = {
        'path': rel_path,
        'name': payload.get('name'),
        'valid': valid,
        'issues': issues,
        'steps': [],
    }
    if not valid:
        return summary

    env = os.environ.copy()
    env.setdefault('PYTHONPATH', str(BASE_DIR))

    for step in payload.get('steps', []):
        step_entry = {
            'name': step.get('name'),
            'cmd': step.get('cmd'),
            'executed': False,
            'success': None,
            'output': None,
        }
        if execute:
            try:
                result = subprocess.run(
                    step['cmd'],
                    shell=True,
                    check=True,
                    executable='/bin/bash',
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                step_entry['executed'] = True
                step_entry['success'] = True
                step_entry['output'] = result.stdout.strip()
            except subprocess.CalledProcessError as exc:
                step_entry['executed'] = True
                step_entry['success'] = False
                step_entry['output'] = exc.output.strip() if exc.output else str(exc)
        summary['steps'].append(step_entry)
    return summary


def main():
    parser = argparse.ArgumentParser(description='Validate workflow plans for Phase F')
    parser.add_argument('workflows', nargs='+', type=Path)
    parser.add_argument('--execute', action='store_true', help='Execute validated steps to simulate Phase F scenario')
    args = parser.parse_args()

    summaries = []
    for wf_path in args.workflows:
        if not wf_path.exists():
            summaries.append({'path': str(wf_path), 'valid': False, 'issues': [f'{wf_path} not found'], 'steps': []})
            continue
        wf_summary = run_workflow(wf_path, execute=args.execute)
        summaries.append(wf_summary)
        _append_log(LOG_FILE, {
            'ts': _timestamp(),
            'workflow': wf_summary['path'],
            'valid': wf_summary['valid'],
            'issues': wf_summary['issues'],
            'executed_steps': sum(1 for s in wf_summary['steps'] if s['executed']),
        })

    overall = {
        'ts': _timestamp(),
        'phase': 'Phase F plan validation',
        'status': 'ok' if all(s['valid'] for s in summaries) else 'fail',
        'workflows': [{'path': s['path'], 'valid': s.get('valid'), 'issues': s.get('issues')} for s in summaries],
    }
    _append_log(SUMMARY_LOG, overall)
    print(json.dumps(overall, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
