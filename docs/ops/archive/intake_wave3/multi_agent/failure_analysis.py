import argparse,json

def run_test():
    return {'status':'ok','root_agent':'executor','confidence':0.78}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
