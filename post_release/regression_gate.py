import argparse
import json
import subprocess

COMMANDS = [
    'python3 -m post_release.incident_triage --test',
    'python3 -m post_release.recovery_playbook --test',
    'python3 -m post_release.slo_evaluator --test',
    'python3 -m post_release.release_gate_v2 --test',
    'python3 -m post_release.canary_gate --test',
    'python3 -m post_release.rollback_advisor --test',
    'python3 -m post_release.incident_timeline --test',
    'python3 -m post_release.ops_packager --test',
]


def run_test() -> dict:
    results = []
    ok = True
    for cmd in COMMANDS:
        p = subprocess.run(cmd.split(), capture_output=True, text=True, check=False)
        r = {'cmd': cmd, 'exit_code': p.returncode}
        results.append(r)
        if p.returncode != 0:
            ok = False
    return {'status': 'ok' if ok else 'failed', 'strict': True, 'results': results}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    out = run_test() if a.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
    if a.test and out.get('status') != 'ok':
        raise SystemExit(1)
