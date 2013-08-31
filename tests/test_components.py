from unittest import TestCase

from mock import patch, Mock

from yape.manager import Manager
from yape.components import Component, LoadableComponent


class PlayerComponent(Component):

    def clean(self, data):
        if len(data['inventory']) != data['inventory_size']:
            self.errors.append('Inventory size does not match inventory')
            return False
        return True

    def post_process(self):
        self.post_process_called = True


class ComponentTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = Manager(self.path)

    def test_init(self):
        data = {
            'inventory': [1, 2],
            'inventory_size': 2,
            'level': 3,
        }
        component = PlayerComponent(self.manager, data)
        self.assertEqual(component.level, 3)
        self.assertEqual(component.inventory, [1, 2])
        self.assertEqual(component.errors, [])

    def test_invalid_data_init(self):
        data = {
            'inventory': [1, 2],
            'inventory_size': 3,
        }
        component = PlayerComponent(self.manager, data)
        self.assertEqual(
            component.errors, ['Inventory size does not match inventory']
        )
        self.assertFalse(getattr(component, 'inventory', None) == [1, 2])

    @patch('yape.components.BaseComponent.process_auto_fields')
    @patch('yape.components.BaseComponent.process_data')
    @patch('yape.components.BaseComponent.is_valid')
    def test_load(self, mock_is_valid, mock_process_data, mock_process_auto):
        mock_is_valid.return_value = True
        data = {
            'inventory': [1, 2],
            'inventory_size': 2,
        }
        player = PlayerComponent(self.manager)
        player.load(data)
        self.assertEqual(player.errors, [])
        mock_is_valid.assert_called_once_with(data)
        mock_process_data.assert_called_once_with(data)
        mock_process_auto.assert_called_once()
        self.assertTrue(player.post_process_called)

    def test_is_valid(self):
        fakeschema = Mock()
        fakeschema.find_errors.return_value = []
        PlayerComponent.schema = fakeschema
        PlayerComponent.clean = Mock(True)
        PlayerComponent.clean_inventory = Mock(
            __name__='clean_inventory', return_value=True
        )
        PlayerComponent.clean_inventory_size = Mock(
            __name__='clean_inventory_size', return_value=True
        )
        data = {
            'inventory': [1, 2],
            'inventory_size': 2,
        }
        player = PlayerComponent(self.manager)
        player.is_valid(data)
        player.schema.find_errors.assert_called_once_with(data)
        player.clean_inventory.assert_called_once_with([1, 2])
        player.clean_inventory_size.assert_called_once_with(2)
        player.clean.assert_called_once_with(data)

    def test_is_valid_field_invalid(self):
        PlayerComponent.clean_inventory = Mock(
            __name__='clean_inventory', return_value=False,
        )
        data = {
            'inventory': [1, 2],
            'inventory_size': 2,
        }
        player = PlayerComponent(self.manager)
        valid = player.is_valid(data)
        self.assertFalse(valid)
        self.assertEqual(player.errors, ['inventory was not valid'])

    def test_is_valid_clean_False(self):
        PlayerComponent.clean = Mock(return_value=False)
        data = {
            'inventory': [1, 2],
        }
        player = PlayerComponent(self.manager)
        valid = player.is_valid(data)
        self.assertFalse(valid)
        self.assertEqual(player.errors, ['{0} did not validate'.format(data)])

    def test_process_auto_fields(self):
        self.fail('Not yet written')


class MapComponent(LoadableComponent):
    location = 'maps'


class LoadableComponentTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = Manager(self.path)

    @patch('yape.manager.Manager.get_json')
    def test_init(self, mock_get_json):
        self.fail('Not yet written')

    @patch('yape.manager.Manager.get_json')
    def test_load_location(self, mock_get_json):
        self.fail('Not yet written')
