from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    # Task is the persistent unit of work moving through the Command Center.
    # It carries the original request, tracks execution state, and stores the
    # results produced by the execution pipeline.
    prompt: str

    # Every Task gets its own identifier so events and other system components
    # can refer to the exact piece of work being executed.
    id: str = field(default_factory=lambda: str(uuid4()))

    # A Task starts pending and is transitioned by the Executor as execution
    # begins, succeeds, or fails.
    status: TaskStatus = TaskStatus.PENDING

    # Results belong to the Task because they are the accumulated output of
    # its execution. default_factory gives each Task its own list instead of
    # accidentally sharing one list between Task instances.
    results: list[object] = field(default_factory=list)