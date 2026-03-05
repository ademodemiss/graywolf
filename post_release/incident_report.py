import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def run_test():
    outdir=Path('/home/adem/graywolf/reports'); outdir.mkdir(parents=True,exist_ok=True)
    ts=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=outdir/f'incident_report_{ts}.json'
    payload={'status':'ok','ts':ts,'summary':'incident timeline generated'}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','artifact':str(out)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
