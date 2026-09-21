from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass
class Event:
    type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: dict = field(default_factory=dict)