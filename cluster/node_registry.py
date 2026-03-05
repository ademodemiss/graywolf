import argparse,json
from pathlib import Path
OUT=Path('/home/adem/graywolf/cluster/nodes.json')
def run_test():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    data={'status':'ok','nodes':[{'id':'node-1','state':'active'}]}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','artifact':str(OUT)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
