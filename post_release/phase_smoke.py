import argparse
import json


def run_test(phase: int) -> dict:
    return {'status': 'ok', 'phase': phase}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--phase', type=int, required=True)
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test(args.phase) if args.test else {'status': 'idle', 'phase': args.phase}
    print(json.dumps(out, ensure_ascii=False))
