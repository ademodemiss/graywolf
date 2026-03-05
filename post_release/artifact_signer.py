import argparse, json, hashlib
from pathlib import Path

OUT=Path('/home/adem/graywolf/release/signature.json')
SRC=Path('/home/adem/graywolf/docs/RELEASE_EVIDENCE.md')

def run_test():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    data=SRC.read_bytes() if SRC.exists() else b''
    sig={'status':'ok','sha256':hashlib.sha256(data).hexdigest(),'source':str(SRC)}
    OUT.write_text(json.dumps(sig,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','artifact':str(OUT)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
