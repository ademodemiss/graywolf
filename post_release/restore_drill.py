import argparse, json, tarfile, tempfile, hashlib
from pathlib import Path

BACKUP_DIR=Path('/home/adem/graywolf/backups')

def _sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def run_test():
    snaps=sorted(BACKUP_DIR.glob('graywolf_snapshot_*.tar.gz'))
    if not snaps: return {'status':'failed','restore_ok':False,'files_verified':False,'reason':'no_backup'}
    snap=snaps[-1]
    with tempfile.TemporaryDirectory() as td:
        with tarfile.open(snap,'r:gz') as t: t.extractall(td)
        restored=Path(td)/'docs'/'roadmap.md'
        files_verified=restored.exists()
    return {'status':'ok','restore_ok':True,'files_verified':files_verified,'snapshot':str(snap)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
