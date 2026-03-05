import argparse,json
from pathlib import Path
OUT=Path('/home/adem/graywolf/cluster/health_summary.json')
def run_test():
    out={'status':'ok','healthy_nodes':1,'unhealthy_nodes':0}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','artifact':str(OUT)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
