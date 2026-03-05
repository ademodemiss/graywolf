import argparse, json, subprocess

def run_test():
    p=subprocess.run(['systemctl','is-active','graywolf'],capture_output=True,text=True,check=False)
    state=(p.stdout or '').strip() or 'unknown'
    return {'status':'ok','service_state':state,'restart_test':'guarded_only'}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
