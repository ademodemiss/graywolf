import argparse, json, hashlib
from pathlib import Path

CFG=Path('/home/adem/graywolf/.env.example')
BASE=Path('/home/adem/graywolf/post_release/config_baseline.sha256')

def run_test():
    cur=hashlib.sha256(CFG.read_bytes()).hexdigest() if CFG.exists() else 'missing'
    old=BASE.read_text(encoding='utf-8').strip() if BASE.exists() else ''
    drift=bool(old and old!=cur)
    BASE.write_text(cur,encoding='utf-8')
    return {'status':'warn' if drift else 'ok','drift':drift,'checksum':cur}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
