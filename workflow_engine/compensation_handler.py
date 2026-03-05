import argparse
import json


def execute_with_compensation(steps: list[dict]) -> dict:
    done = []
    compensation = []
    for s in steps:
        if s.get('fail'):
            for c in reversed(compensation):
                c()
            return {'status': 'compensated', 'completed': done}
        done.append(s.get('name'))
        if 'compensate' in s and callable(s['compensate']):
            compensation.append(s['compensate'])
    return {'status': 'completed', 'completed': done}


def run_test() -> dict:
    marks = []

    def c1():
        marks.append('undo_s1')

    def c2():
        marks.append('undo_s2')

    steps = [
        {'name': 's1', 'compensate': c1},
        {'name': 's2', 'compensate': c2},
        {'name': 's3', 'fail': True},
    ]
    out = execute_with_compensation(steps)
    return {'status': out['status'], 'compensated_order_ok': marks == ['undo_s2', 'undo_s1']}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle'}, ensure_ascii=False))
