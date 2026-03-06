import argparse
import json
from pathlib import Path

INDEX_FILE = Path('/home/adem/graywolf/reports/artifact_index.json')


def _load_artifacts(base_dir: Path) -> list[dict]:
    artifacts = []
    for f in base_dir.rglob('*.json'):
        if f.name.startswith('task_') or f.name.startswith('ops_'):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                artifacts.append({
                    'path': str(f.relative_to(base_dir.parent)),
                    'id': data.get('task_id') or data.get('id'),
                    'phase': data.get('phase'),
                    'status': data.get('status'),
                    'final_status': data.get('final_status'),
                    'ts': data.get('ts'),
                })
            except Exception:
                pass
    return artifacts


def run_test(query: str = None) -> dict:
    base_dir = Path('/home/adem/graywolf/reports')
    all_artifacts = _load_artifacts(base_dir)

    if query:
        results = [a for a in all_artifacts if query.lower() in str(a).lower()]
    else:
        results = all_artifacts

    out = {
        'status': 'ok',
        'total_artifacts': len(all_artifacts),
        'query_results': len(results),
        'results': results,
    }
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(INDEX_FILE)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--query', type=str)
    a = p.parse_args()
    print(json.dumps(run_test(query=a.query) if a.test else {'status': 'idle'}, ensure_ascii=False))
