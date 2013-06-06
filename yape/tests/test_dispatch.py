from unittest import TestCase

from mock import Mock, MagicMock, call

from yape.fsm import FSM
from yape.dispatch import Dispatcher, get_pygame_event_queue


class DispatcherTestCase(TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher(get_pygame_event_queue)

    def create_fsm(self):
        transitions = [
            {
                'name': 'start',
                'source': 'menu',
                'destination': 'main'
            },
            {
                'name': 'open_menu',
                'source': 'main',
                'destination': 'menu'
            },
        ]
        return FSM('main', transitions)

    def test_register_one_with_event_type(self):
        event_type = 1
        listener_a, listener_b = Mock(), Mock()
        self.dispatcher.register('main', listener_a, event_type)
        self.dispatcher.register('menu', listener_b, event_type)
        listeners = self.dispatcher.listeners
        self.assertEqual(listeners[('main', event_type)], set([listener_a]))
        self.assertEqual(listeners[('menu', event_type)], set([listener_b]))

    def test_register_multiple_with_event_type(self):
        event_type = 1
        listener_a, listener_b, listener_c = Mock(), Mock(), Mock()
        self.dispatcher.register('main', listener_a, event_type)
        self.dispatcher.register('main', listener_b, event_type)
        self.dispatcher.register('main', listener_c, event_type)
        listeners = self.dispatcher.listeners
        main_listeners = listeners[('main', event_type)]
        self.assertEqual(
            main_listeners, set([listener_a, listener_b, listener_c])
        )

    def test_register_varied(self):
        event_type = 1
        listener_a, listener_b, listener_c = Mock(), Mock(), Mock()
        self.dispatcher.register('main', listener_a, event_type)
        self.dispatcher.register('main', listener_b, event_type)
        self.dispatcher.register('menu', listener_c, event_type)
        listeners = self.dispatcher.listeners
        main_listeners = listeners[('main', event_type)]
        menu_listeners = listeners[('menu', event_type)]
        self.assertEqual(
            main_listeners, set([listener_a, listener_b])
        )
        self.assertEqual(
            menu_listeners, set([listener_c])
        )

    def test_register_no_event_type(self):
        listener_a, listener_b, listener_c = Mock(), Mock(), Mock()
        self.dispatcher.register('main', listener_a)
        self.dispatcher.register('main', listener_b)
        self.dispatcher.register('menu', listener_c)
        listeners = self.dispatcher.listeners
        main_listeners = listeners[('main', None)]
        menu_listeners = listeners[('menu', None)]
        self.assertEqual(
            main_listeners, set([listener_a, listener_b])
        )
        self.assertEqual(
            menu_listeners, set([listener_c])
        )

    def test_register_listener_no_event_type(self):

        @self.dispatcher.register_listener(['main', 'menu'])
        def listener_a(event, game_data, *args, **kwargs):
            pass

        @self.dispatcher.register_listener(['main'])
        def listener_b(event, game_data, *args, **kwargs):
            pass

        self.assertEqual(
            self.dispatcher.listeners, {
                ('main', None): set([listener_a, listener_b]),
                ('menu', None): set([listener_a])
            }
        )

    def test_register_listener_with_event_type(self):

        @self.dispatcher.register_listener(['main', 'menu'], 1)
        def listener_a(event, game_data, *args, **kwargs):
            pass

        @self.dispatcher.register_listener(['main'], 1)
        def listener_b(event, game_data, *args, **kwargs):
            pass

        self.assertEqual(
            self.dispatcher.listeners, {
                ('main', 1): set([listener_a, listener_b]),
                ('menu', 1): set([listener_a])
            }
        )

    def test_dispatch_on_state(self):
        fsm = self.create_fsm()
        mock_game_data = MagicMock(state=fsm)
        mock_event_1 = MagicMock(event_type=1)
        mock_event_2 = MagicMock(event_type=2)
        listener_a, listener_b, listener_c = Mock(), Mock(), Mock()
        self.dispatcher.register('main', listener_a)
        self.dispatcher.register('main', listener_b)
        self.dispatcher.register('menu', listener_c)
        self.dispatcher.dispatch(mock_event_1, mock_game_data)
        # FSM is in the main state, listeners a and b should be called
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 1)
        self.assertEqual(
            listener_c.call_count, 0
        )
        mock_game_data.state.open_menu()
        # FSM is in the menu state, listener c should be called
        self.dispatcher.dispatch(mock_event_1, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 1)
        self.assertEqual(listener_c.call_count, 1)

    def test_dispatch_on_event_type(self):
        fsm = self.create_fsm()
        mock_game_data = MagicMock(state=fsm)
        mock_event_1 = MagicMock(type=1)
        mock_event_2 = MagicMock(type=2)
        listener_a, listener_b, listener_c, listener_d = Mock(), Mock(), Mock(), Mock()
        self.dispatcher.register('main', listener_a, 1)
        self.dispatcher.register('main', listener_b, 2)
        self.dispatcher.register('menu', listener_c, 1)
        self.dispatcher.register('menu', listener_d, 2)
        # each state and event type are uniquely paired for each listener
        self.dispatcher.dispatch(mock_event_1, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 0)
        self.assertEqual(listener_c.call_count, 0)
        self.assertEqual(listener_d.call_count, 0)
        self.dispatcher.dispatch(mock_event_2, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 1)
        self.assertEqual(listener_c.call_count, 0)
        self.assertEqual(listener_d.call_count, 0)
        mock_game_data.state.open_menu()
        self.dispatcher.dispatch(mock_event_1, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 1)
        self.assertEqual(listener_c.call_count, 1)
        self.assertEqual(listener_d.call_count, 0)
        self.dispatcher.dispatch(mock_event_2, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 1)
        self.assertEqual(listener_c.call_count, 1)
        self.assertEqual(listener_d.call_count, 1)

    def test_dispatch_to_multiple_listeners(self):
        fsm = self.create_fsm()
        mock_game_data = MagicMock(state=fsm)
        mock_event_1 = MagicMock(type=1)
        mock_event_2 = MagicMock(type=2)
        listener_a, listener_b, listener_c, listener_d = Mock(), Mock(), Mock(), Mock()
        self.dispatcher.register('main', listener_a, 1)
        self.dispatcher.register('main', listener_b, 2)
        self.dispatcher.register('main', listener_c, 1)
        self.dispatcher.register('main', listener_d)
        self.dispatcher.dispatch(mock_event_1, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 0)
        self.assertEqual(listener_c.call_count, 1)
        self.assertEqual(listener_d.call_count, 1)
        self.dispatcher.dispatch(mock_event_2, mock_game_data)
        self.assertEqual(listener_a.call_count, 1)
        self.assertEqual(listener_b.call_count, 1)
        self.assertEqual(listener_c.call_count, 1)
        self.assertEqual(listener_d.call_count, 2)

    def test_dispatch_args_kwargs(self):
        fsm = self.create_fsm()
        mock_game_data = MagicMock(state=fsm)
        mock_event_1 = MagicMock(type=1)
        listener_a = Mock()
        self.dispatcher.register('main', listener_a)
        self.dispatcher.dispatch(mock_event_1, mock_game_data, this=1)
        self.dispatcher.dispatch(mock_event_1, mock_game_data, other=2)
        call_1, call_2 = listener_a.call_args_list
        self.assertEqual(call_1, call(mock_event_1, mock_game_data, this=1))
        self.assertEqual(call_2, call(mock_event_1, mock_game_data, other=2))

    def test_handle_events_no_events(self):
        fsm = self.create_fsm()
        mock_game_data = MagicMock(state=fsm)
        mock_event_1 = MagicMock(type=1)
        listener_a = Mock()
        get_event_queue = Mock()
        get_event_queue.return_value = []
        dispatcher = Dispatcher(get_event_queue)
        dispatcher.register('main', listener_a)
        dispatcher.handle_events(mock_game_data)
        self.assertFalse(listener_a.called)

    def test_handle_events_many_events(self):
        fsm = self.create_fsm()
        mock_game_data = MagicMock(state=fsm)
        # Create 3 types of mock events
        mock_events = MagicMock(type=1), MagicMock(type=2), MagicMock(type=3)
        mock_event_1, mock_event_2, mock_event_3 = mock_events
        # Create a listener to correspond with each mock event
        listeners = Mock(), Mock(), Mock()
        listener_a, listener_b, listener_c = listeners
        # Put the three mock events into the event queue and register listeners
        get_event_queue = Mock()
        get_event_queue.return_value = mock_events
        dispatcher = Dispatcher(get_event_queue)
        dispatcher.register('main', listener_a, 1)
        dispatcher.register('main', listener_b, 2)
        dispatcher.register('main', listener_c, 3)
        # Assure each listener is called with its corresponding mock_event
        dispatcher.handle_events(mock_game_data)
        for listener, mock_event in zip(listeners, mock_events):
            self.assertEqual(
                listener.call_args, call(mock_event, mock_game_data),
                'listener {0} should be called with {1} and {2}'.format(
                    listener, mock_event, mock_game_data
                )
            )

