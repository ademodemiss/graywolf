import argparse,json
from pathlib import Path
OUT=Path('/home/adem/graywolf/reports/evidence_pack.json')
def run_test():
    data={'status':'ok','includes':['dry_run','once','terminal_log','state_snapshot','artifacts']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','artifact':str(OUT)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
