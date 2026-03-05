import argparse, json, hashlib
from pathlib import Path

LOG=Path('/home/adem/graywolf/logs/terminal.log')

def run_test():
    lines=LOG.read_text(encoding='utf-8').splitlines() if LOG.exists() else []
    ok_order=True
    ts_prev=''
    for ln in lines[-200:]:
        try: obj=json.loads(ln); ts=obj.get('ts','')
        except Exception: continue
        if ts_prev and ts<ts_prev: ok_order=False
        ts_prev=ts
    digest=hashlib.sha256(LOG.read_bytes()).hexdigest() if LOG.exists() else None
    return {'status':'ok' if ok_order else 'warn','sha256':digest,'ordered':ok_order}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
