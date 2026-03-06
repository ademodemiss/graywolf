import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CHAIN_FILE = Path('/home/adem/graywolf/reports/evidence_chain.json')
REPORT_FILE = Path('/home/adem/graywolf/reports/evidence_integrity_chain_report.json')
TARGET = Path('/home/adem/graywolf/reports/task_diff_aware_commit_report.json')


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_chain() -> list:
    if not CHAIN_FILE.exists():
        return []
    try:
        data = json.loads(CHAIN_FILE.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_chain(chain: list):
    CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHAIN_FILE.write_text(json.dumps(chain, ensure_ascii=False, indent=2), encoding='utf-8')


def append_entry(target: Path) -> dict:
    chain = _load_chain()
    parent_hash = chain[-1]['hash'] if chain else None
    digest = _digest(target)
    entry = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'chain_id': 'evidence-chain-v1',
        'path': str(target),
        'content_digest': digest,
        'parent_hash': parent_hash,
    }
    base = f"{entry['ts']}|{entry['chain_id']}|{entry['path']}|{entry['content_digest']}|{entry['parent_hash']}"
    entry['hash'] = hashlib.sha256(base.encode('utf-8')).hexdigest()
    chain.append(entry)
    _save_chain(chain)
    return entry


def verify_chain() -> dict:
    chain = _load_chain()
    if not chain:
        return {'ok': False, 'reason': 'empty_chain'}
    prev = None
    for i, e in enumerate(chain):
        if e.get('parent_hash') != prev:
            return {'ok': False, 'reason': 'parent_mismatch', 'index': i}
        base = f"{e.get('ts')}|{e.get('chain_id')}|{e.get('path')}|{e.get('content_digest')}|{e.get('parent_hash')}"
        expected = hashlib.sha256(base.encode('utf-8')).hexdigest()
        if e.get('hash') != expected:
            return {'ok': False, 'reason': 'hash_mismatch', 'index': i}
        prev = e.get('hash')
    return {'ok': True, 'entries': len(chain)}


def run_test() -> dict:
    if not TARGET.exists():
        return {'status': 'failed', 'reason': 'missing_target', 'target': str(TARGET)}

    first = append_entry(TARGET)
    verify_ok = verify_chain()

    # determinism: same content digest for same file now
    digest1 = _digest(TARGET)
    digest2 = _digest(TARGET)
    same_digest = digest1 == digest2

    # tamper detection simulation (in-memory)
    chain = _load_chain()
    tamper_detected = True
    if chain:
        chain_bad = [dict(x) for x in chain]
        chain_bad[-1]['content_digest'] = 'tampered'
        prev = None
        tamper_detected = False
        for i, e in enumerate(chain_bad):
            base = f"{e.get('ts')}|{e.get('chain_id')}|{e.get('path')}|{e.get('content_digest')}|{e.get('parent_hash')}"
            expected = hashlib.sha256(base.encode('utf-8')).hexdigest()
            if e.get('hash') != expected or e.get('parent_hash') != prev:
                tamper_detected = True
                break
            prev = e.get('hash')

    out = {
        'status': 'ok' if verify_ok.get('ok') and same_digest and tamper_detected else 'failed',
        'latest_entry': first,
        'chain_verify': verify_ok,
        'same_digest_check': same_digest,
        'tamper_detected': tamper_detected,
        'chain_file': str(CHAIN_FILE),
    }
    REPORT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT_FILE)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    if a.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    elif a.verify:
        print(json.dumps(verify_chain(), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle'}, ensure_ascii=False))
