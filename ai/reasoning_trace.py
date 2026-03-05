import argparse,json
from pathlib import Path
LOG=Path('/home/adem/graywolf/logs/agent_reasoning.log')
def run_test():
    LOG.parent.mkdir(parents=True,exist_ok=True)
    LOG.write_text('plan->execute->review\\n',encoding='utf-8')
    return {'status':'ok','artifact':str(LOG)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
