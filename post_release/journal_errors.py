import argparse, json, subprocess

WORDS=['error','failed','exception']

def run_test():
    p=subprocess.run(['journalctl','-u','graywolf','-n','120','--no-pager'],capture_output=True,text=True,check=False)
    t=(p.stdout or '').lower(); counts={w:t.count(w) for w in WORDS}; total=sum(counts.values())
    sev='error' if total>10 else 'warn' if total>0 else 'ok'
    return {'status':sev,'counts':counts,'total':total}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
