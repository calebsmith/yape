from unittest import TestCase

from mock import Mock

from yape.fsm import FSM


class FSMTestCase(TestCase):

    def setUp(self):
        # Create a door to test.
        self.door_transitions = [
            {
                'name': 'open',
                'source': 'closed',
                'destination': 'opened',
            },
            {
                'name': 'close',
                'source': 'opened',
                'destination': 'closed',
            },
            {
                'name': 'lock',
                'source': 'closed',
                'destination': 'locked',
            },
            {
                'name': 'unlock',
                'source': 'locked',
                'destination': 'closed',
            },
        ]
        self.open_callback = Mock()

        self.door_callbacks = {
            'on_open': self.open_callback,
        }
        self.door = FSM('opened', self.door_transitions, self.door_callbacks)


    def assertCanOnly(self, fsm, transition_names):
        transition_names = set(transition_names)
        possible_transitions = fsm._source_to_names[fsm.state]
        err_msg = 'The FSM can {0} from the current state, expected to capable of: {1}'
        self.assertEqual(
            transition_names, possible_transitions,
            err_msg.format(possible_transitions, transition_names)
        )

    def test_possible_states(self):
        self.assertEqual(
            self.door.possible_states, set(['opened', 'closed', 'locked']),
        )

    def test_transitions(self):
        # Transitions are stored/reported in the format:
        #     ('source', 'name'): 'destination'
        expected_transitions = {
            ('closed', 'open'): 'opened',
            ('closed', 'lock'): 'locked',
            ('locked', 'unlock'): 'closed',
            ('opened', 'close'): 'closed'
        }
        try:
            self.door.open()
            self.fail('IllegalTransitionException should be raised')
        except FSM.IllegalTransitionException:
            self.assertTrue(True)
        self.assertEqual(self.door.transitions, expected_transitions)

    def test_valid_transition_calls(self):
        self.assertTrue(self.door.is_state('opened'))
        self.assertCanOnly(self.door, ['close'])
        self.door.close()
        self.assertTrue(self.door.is_state('closed'))
        self.assertCanOnly(self.door, ['open', 'lock'])
        self.door.lock()
        self.assertTrue(self.door.is_state('locked'))
        self.assertCanOnly(self.door, ['unlock'])
        self.door.unlock()
        self.assertTrue(self.door.is_state('closed'))
        self.assertCanOnly(self.door, ['open', 'lock'])
        self.door.open()
        self.assertTrue(self.door.is_state('opened'))
        self.assertCanOnly(self.door, ['close'])

    def test_invalid_transition_calls(self):
        try:
            self.door.lock()
            self.fail('IllegalTransitionExcept should be raised')
        except FSM.IllegalTransitionException:
            self.assertTrue(True)

        self.door.close()
        self.door.lock()
        try:
            self.door.open()
            self.fail('IllegalTransitionExcept should be raised')
        except FSM.IllegalTransitionException:
            self.assertTrue(True)

    def test_add_transition(self):
        self.door.add_transition({
            'name': 'bash',
            'source': 'locked',
            'destination': 'bashed',
        })
        self.assertTrue('bashed' in self.door.possible_states)
        self.door.close()
        self.door.lock()
        self.assertCanOnly(self.door, ['unlock', 'bash'])
        self.door.bash()
        self.assertTrue(self.door.is_state('bashed'))
        self.assertCanOnly(self.door, [])
        self.door.add_transition({
            'name': 'repair',
            'source': 'bashed',
            'destination': 'locked'
        })
        self.assertCanOnly(self.door, ['repair'])
        self.door.repair()
        self.assertTrue(self.door.is_state('locked'))

    def test_add_transition_many_to_one(self):
        self.door.add_transition({
            'name': 'seal',
            'source': 'closed',
            'destination': 'sealed',
        })
        self.door.add_transition({
            'name': 'seal',
            'source': 'locked',
            'destination': 'sealed',
        })
        self.door.close()
        self.door.seal()
        self.assertTrue(self.door.is_state('sealed'))
        self.door.state = 'closed'
        self.door.lock()
        self.door.seal()
        self.assertTrue(self.door.is_state('sealed'))
        self.door.state = 'opened'
        try:
            self.door.seal()
            self.fail('IllegalTransitionException should be raised')
        except FSM.IllegalTransitionException:
            self.assertTrue(True)

    def test_invalid_transition_name(self):
        try:
            # shadows a builtin
            self.door.add_transition({
                'name': '__dict__',
                'source': 'opened',
                'destination': 'closed',
            })
            self.fail('IllegalNameException should be raised')
        except FSM.IllegalNameException:
            self.assertTrue(True)
        try:
            # shadows a method name on FSM
            self.door.add_transition({
                'name': 'transitions',
                'source': 'closed',
                'destination': 'opened',
            })
            self.fail('IllegalNameException should be raised')
        except FSM.IllegalNameException:
            self.assertTrue(True)

    def test_invalid_transition_override(self):
        try:
            self.door.add_transition({
                'name': 'close',
                'source': 'opened',
                'destination': 'locked',
            })
            self.fail('IllegalNameException should be raised')
        except FSM.IllegalNameException:
            self.assertTrue(True)

    def test_callback_called(self):
        self.assertEquals(self.open_callback.call_count, 0)
        self.door.close()
        self.assertEquals(self.open_callback.call_count, 0)
        self.door.open()
        self.assertEquals(self.open_callback.call_count, 1)
        self.door.close()
        self.door.open()
        self.assertEquals(self.open_callback.call_count, 2)

    def test_add_callback(self):
        close_callback = Mock()
        self.door.close()
        self.assertEqual(close_callback.call_count, 0)
        self.door.open()
        self.door.add_callback('on_close', close_callback)
        self.door.close()
        self.assertEqual(close_callback.call_count, 1)

    def test_callback_return_and_args_kwargs(self):

        def close_callback(a, b, data=None):
            a.append(1)
            b.append(2)
            data.update({'a': 1})
            return 'b'

        self.door.add_callback('on_close', close_callback)
        list_a = []
        list_b = []
        data = {}
        expected_return_value = self.door.close(list_a, list_b, data=data)
        self.assertEqual(
            list_a, [1],
            'The callback should append 1 to the first argument as a side-effect'
        )
        self.assertEqual(
            list_b, [2],
            'The callback should append 2 to the first argument as a side-effect'
        )
        self.assertEqual(
            data, {'a': 1},
            'The callback should update the `data` kwarg with {"a": 1} as a side-effect'
        )
        self.assertEqual(
            expected_return_value, 'b', 'The callback should return "b"'
        )

    def test_on_before_callback(self):

        before_open_callback = Mock(return_value=True)
        before_lock_callback = Mock(return_value=False)

        self.door.add_callback('on_before_open', before_open_callback)
        self.door.add_callback('on_before_lock', before_lock_callback)
        self.door.close()
        self.door.open()
        self.assertTrue(
            self.door.is_state('opened'),
             'on_before returned True but transition did not occur'
        )
        self.assertEqual(before_open_callback.call_count, 1)
        self.door.close()
        self.door.lock()
        self.assertTrue(
            self.door.is_state('closed'),
             'on_before returned False but transition still occured'
        )

    def test_illegal_callback_name(self):
        try:
            self.door.add_callback('on_knock', lambda: True)
            self.fail('IllegalCallbackException should be raised')
        except FSM.IllegalCallbackException:
            self.assertTrue(True)
