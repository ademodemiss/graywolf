import argparse, json, tarfile
from datetime import datetime, timezone
from pathlib import Path

BACKUP_DIR=Path('/home/adem/graywolf/backups'); ROOT=Path('/home/adem/graywolf')

def run_test():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=BACKUP_DIR/f'graywolf_snapshot_{ts}.tar.gz'
    with tarfile.open(out,'w:gz') as t:
        for rel in ['memory','logs','docs/roadmap.md','.env.example']:
            p=ROOT/rel
            if p.exists(): t.add(p, arcname=rel)
    return {'status':'ok','artifact':str(out),'exists':out.exists()}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
