import argparse, json
from pathlib import Path

OUT=Path('/home/adem/graywolf/metrics/ops_metrics_latest.json')

def _load(p):
    pp=Path(p)
    if not pp.exists(): return {}
    try:return json.loads(pp.read_text(encoding='utf-8'))
    except Exception:return {}

def run_test():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out={'status':'ok','ops_monitor':_load('/home/adem/graywolf/post_release/ops_summary_latest.json'),'heartbeat':_load('/home/adem/graywolf/post_release/heartbeat_snapshot.json')}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','artifact':str(OUT)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
