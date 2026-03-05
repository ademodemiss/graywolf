import argparse, json

def run_test():
    policy={'warn_threshold':1,'error_threshold':5,'routes':{'warn':'stdout','error':'stdout'}}
    return {'status':'ok','policy':policy}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
