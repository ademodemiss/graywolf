import argparse,json

def run_test():
    q=['a','b']; done=q.pop(0)
    return {'status':'ok','queue_len':len(q),'processed':done}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
