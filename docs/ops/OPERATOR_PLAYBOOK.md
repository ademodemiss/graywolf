# Graywolf Operator Playbook

## 1) Komut gönderme
Endpoint: `POST /api/command`

Örnek body:
```json
{
  "intent": "healthcheck",
  "payload": {"goal": "günlük healthcheck"},
  "source": "api"
}
```

Yanıt durumları:
- `queued`: komut doğrudan kuyruğa alındı
- `confirm_required`: onay bekliyor (`approval_request.request_id` döner)
- `denied`: politika reddetti

## 2) Onay callback işleme
Endpoint: `POST /api/approval/callback`

Örnek body:
```json
{
  "callback_data": "approval.grant:APR-20260318...",
  "actor": "operator"
}
```

Desteklenen aksiyonlar:
- `approval.grant:<request_id>`
- `approval.deny:<request_id>`
- `approval.skip:<request_id>`

## 3) Runtime durum kontrolü
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python -m core.runtime status --session-id ops
```

Kontrol edilecek alanlar:
- `approval.pending_command_approvals`
- `queue.queue_depth`
- `queue.last_5_queued`
- `queue.last_5_processed`

## 4) Pre-release zorunlu gate
```bash
/home/adem/graywolf/scripts/release_precheck.sh
```
PASS olmadan release yok.

## 5) Günlük operasyon
```bash
/home/adem/graywolf/scripts/ops_automation.sh daily
```

## 6) Queue hijyeni
```bash
PYTHONPATH=/home/adem/graywolf /home/adem/.openclaw/workspace/.venv/bin/python /home/adem/graywolf/scripts/queue_hygiene.py --apply
```
