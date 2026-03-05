# GrayWolf — Target Architecture (Reference)

## Layered Model

```text
[API/Agent Layer]
  ├─ Planner Agent
  ├─ Executor Agent
  └─ Monitor Agent
          │
          ▼
[Event Bus]
  ├─ task.created
  ├─ task.started
  ├─ task.completed
  ├─ task.failed
  ├─ node.joined
  └─ node.dead
          │
          ▼
[Task State Machine + Queue Core]
  ├─ Durable Task Store
  ├─ Guarded State Transitions
  ├─ Lease/Lock Manager
  └─ Dead Letter Queue
          │
          ▼
[Distributed Pull Workers (Cluster Nodes)]
  ├─ pull()
  ├─ execute()
  ├─ heartbeat()
  └─ ack / fail / retry
          │
          ▼
[Workflow Engine]
  ├─ Parser
  ├─ Validator
  ├─ DAG Graph Executor
  └─ Step Runtime
          │
          ▼
[Observability]
  ├─ /system/metrics
  ├─ Alert Manager
  ├─ Performance Reports
  └─ Dashboard / Telegram
```

## Implementation Order (Locked)
1. **Task State Machine** (durable lifecycle + transition guards)
2. **Distributed Pull + Lease/Lock** (remove central scheduler bottleneck)
3. **Real Observability Metrics** (latency/runtime/retry/dead-letter)
4. **Event Bus** (decoupled runtime integration)

## Mandatory Task Model (Minimum)
- `id`
- `status` (`CREATED | QUEUED | RUNNING | COMPLETED | FAILED | DEAD_LETTER`)
- `payload`
- `result`
- `created_at`
- `queued_at`
- `started_at`
- `finished_at`
- `updated_at`
- `retry_count`
- `node_id`
- `locked_by`
- `locked_at`
- `lease_timeout_s`

## Mandatory Metrics (Minimum)
- `queue_depth`
- `queue_latency_ms`
- `avg_task_runtime_ms`
- `scheduler_delay_ms`
- `retry_rate`
- `dead_letter_rate`
- `node_idle_time`
- `active_tasks`
- `node_count`

## Notes
- Keep module coupling low: communicate through events and durable state transitions.
- Never skip state transitions directly (enforce invalid transition guards).
- Node failures must re-queue leased tasks after timeout.
