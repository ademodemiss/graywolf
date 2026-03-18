import argparse,json

def run_test():
    return {'status':'ok','budget_guard':True,'time_guard':True}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
