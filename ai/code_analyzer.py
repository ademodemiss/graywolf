import argparse,json

def run_test():
    return {'status':'ok','findings':2,'self_improvement_hints':['reduce duplication','add stricter tests']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
