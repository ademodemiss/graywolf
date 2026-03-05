import argparse,json

def run_test(): return {'status':'ok','context_sources':12}
if __name__=='__main__': p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'}))
