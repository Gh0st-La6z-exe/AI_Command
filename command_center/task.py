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
    prompt: str

    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    results: list[object] = field(default_factory=list)
   