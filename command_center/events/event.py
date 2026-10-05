from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass
class Event:
    # Event is the system's record of something that happened.
    # It carries the event type plus the information needed by anything
    # listening to that event without coupling those components together.
    type: str

    # Capture the creation time when the Event instance is created.
    # default_factory is required here so each Event gets its own timestamp
    # instead of reusing a timestamp created when the class was defined.
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Event-specific payload. Different event types can carry different data,
    # so the Event doesn't need to know the structure of every possible event.
    data: dict = field(default_factory=dict)