from collections import defaultdict

import pygame


class Dispatcher(object):
    """
    An event dispatcher that registers event listeners and dispatchs events to
    them based on the current game state using a provided event queue.
    """

    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.listeners = defaultdict(set)

    def register(self, state, listener, event_type=None):
        """
        Given a `state` name, a `listener` function, and optionally an
        `event_type`, registers the listener for calling when the game is in
        the given state and the event type occurs. If no `event_type` is given,
        the listener is called whenever the game is in the given state,
        regardless of the event.
        """
        self.listeners[(state, event_type)].add(listener)

    def register_listener(self, states, event_type=None):
        """
        Decorator that registers a listener. Takes a list of state strings to
        register the listener for. Optionally takes an event_type, which is the
        pygame event type that the listener should be called for. If the
        event type is not provided, the listener is called for all event types
        """

        def decorator(f):
            if not getattr(f, 'registered', False):
                for state in states:
                    self.register(state, f, event_type)
                f.registered = True
            return f
        return decorator

    def dispatch(self, event, game_data, *args, **kwargs):
        """
        Given a pygame event, the `game_data`, and any args/kwargs,
        call any listeners that are registered for the state_machine's current
        state paired with the event type. Any args/kwargs are passed to the
        listeners
        """
        typed_listeners = self.listeners[(game_data.state.state, event.type)]
        untyped_listeners = self.listeners[(game_data.state.state, None)]
        listeners = typed_listeners | untyped_listeners
        for listener in listeners:
            listener(event, game_data, *args, **kwargs)

    def handle_events(self, game_data, *args, **kwargs):
        """
        Given the `game_data` and any args/kwargs, dispatch pygame events to
        the registered listeners for the current state based on the event_type
        """
        for event in self.event_queue():
            self.dispatch(event, game_data, *args, **kwargs)


def get_pygame_event_queue():
    return pygame.event.get()


dispatcher = Dispatcher(get_pygame_event_queue)

