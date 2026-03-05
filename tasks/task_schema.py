import argparse,json
from pathlib import Path

def run_test():
    schema={'goal':'str','context':'str','constraints':'list','acceptance_criteria':'list','evidence_requirements':'list'}
    Path('/home/adem/graywolf/tasks/example_task.json').write_text(json.dumps({'goal':'demo','context':'x','constraints':[],'acceptance_criteria':['ok'],'evidence_requirements':['log']},ensure_ascii=False,indent=2),encoding='utf-8')
    return {'status':'ok','schema':schema}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
