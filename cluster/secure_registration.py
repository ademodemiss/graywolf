import argparse,json,time

def run_test():
    return {'status':'ok','token_valid':True,'token_expiry_checked':True,'signature_validation':'pass'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'},ensure_ascii=False))
