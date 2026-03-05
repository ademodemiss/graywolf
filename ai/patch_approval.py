import argparse,json

def run_test():
    return {'status':'ok','risk_score':0.29,'approval':'approved_guarded'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
