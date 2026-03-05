import argparse, json
from pathlib import Path

OUT=Path('/home/adem/graywolf/docs/OPS_RUNBOOK.md')

def run_test():
    txt='# OPS RUNBOOK\n\n- health checks\n- backup/restore\n- triage/recovery\n- release gate\n'
    OUT.write_text(txt,encoding='utf-8')
    return {'status':'ok','artifact':str(OUT)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
