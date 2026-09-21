from .event import Event


class EventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event):
        for handler in self._handlers.get(event.type, []):
            handler(event)