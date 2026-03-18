class EventTypes:
    TASK_CREATED = "task.created"
    TASK_LEASED = "task.leased"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    NODE_JOINED = "node.joined"
    NODE_DEAD = "node.dead"
    NODE_HEARTBEAT = "node.heartbeat"
    NODE_UPDATED = "node.updated"

    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"

    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_GRANTED = "approval.granted"
    APPROVAL_DENIED = "approval.denied"
    APPROVAL_SKIPPED = "approval.skipped"

    REPLAN_READY = "replan.ready"
    REPLAN_EXECUTED = "replan.executed"
