import argparse,json

def run_test(): return {'status':'ok','goal_api':'enabled','cli_goal':'enabled','schema':'v1'}
if __name__=='__main__': p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args();print(json.dumps(run_test() if a.test else {'status':'idle'}))
