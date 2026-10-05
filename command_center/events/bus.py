from .event import Event


class EventBus:
    def __init__(self):
        # EventBus decouples the component producing an event from the
        # components that need to react to it. The emitter does not need
        # to know who is listening or what they will do with the event.
        self._handlers = {}

    def subscribe(self, event_type, handler):
        # Register a handler against an event type. Multiple components can
        # subscribe to the same event without the event producer knowing
        # anything about those subscribers.
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event):
        # Dispatch the event to every handler registered for its type.
        # The bus owns routing; handlers own the behavior that happens
        # in response to the event.
        for handler in self._handlers.get(event.type, []):
            handler(event)