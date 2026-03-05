import argparse, json

def run_test():
    data=['x'*1024]*20000
    return {'status':'warn' if len(data)>0 else 'ok','allocated_blocks':len(data)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
