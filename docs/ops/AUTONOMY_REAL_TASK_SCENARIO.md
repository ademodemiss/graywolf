# Autonomy Real Task Scenario

## 1) Kuyruğa örnek görev ekle
```bash
python3 /home/adem/graywolf/scripts/seed_autonomy_tasks.py
```

## 2) Gerçek queue tasklarını çalıştır (2 görev)
```bash
python3 - <<'PY'
import sys
sys.path.insert(0,'/home/adem/graywolf')
from core.autonomous_loop import AutonomousLoop, LLMAdapter
from core.orchestrator import Orchestrator

class MockLLM(LLMAdapter):
    def generate_response(self,prompt:str,**kwargs):
        return "step1|echo 'Autonomy real queue task'"
    def get_model_info(self): return {"name":"mock"}
    def stream_response(self,prompt:str,**kwargs):
        yield self.generate_response(prompt)
    def chat_completion(self,messages,**kwargs):
        return {"choices":[{"message":{"content":"step1|echo 'Autonomy real queue task'"}}]}

loop=AutonomousLoop(queue_dir='/home/adem/graywolf/tasks/queue', processed_dir='/home/adem/graywolf/tasks/processed', llm=MockLLM())
loop.orchestrator=Orchestrator(loop.llm)
print(loop.run_once())
print(loop.run_once())
PY
```

## 3) Sonuçları kontrol et
- Queue: `/home/adem/graywolf/tasks/queue`
- Processed: `/home/adem/graywolf/tasks/processed`
- Son işlenen task dosyaları `tasks/processed/*.json`

## Not
Önce sağlık kontrolü önerilir:
```bash
/home/adem/graywolf/scripts/daily_healthcheck.sh
```
