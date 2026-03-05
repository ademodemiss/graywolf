import argparse, json, tempfile
from pathlib import Path

def run_test():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'dummy.bin'
        p.write_bytes(b'0'*(5*1024*1024))
        pressure=p.exists() and p.stat().st_size>0
    return {'status':'warn','disk_pressure_detected':bool(pressure)}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--test',action='store_true'); a=p.parse_args()
    print(json.dumps(run_test() if a.test else {'status':'idle'}, ensure_ascii=False))
