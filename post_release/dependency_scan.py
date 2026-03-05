import argparse, json, subprocess

def run_test():
    p=subprocess.run(['pip','check'],capture_output=True,text=True,check=False)
    ok=p.returncode==0
    return {'status':'ok' if ok else 'warn','pip_check_exit':p.returncode}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
