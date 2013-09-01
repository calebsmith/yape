from unittest import TestCase

from mock import patch, Mock

from yape.manager import Manager
from yape.components import Component, LoadableComponent


class PlayerComponent(Component):

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
        class FakeComponent(Component):

            def clean(self, data):
                if len(data['inventory']) != data['inventory_size']:
                    self.errors.append(
                        'Inventory size does not match inventory'
                    )
                    return False
                return True

        data = {
            'inventory': [1, 2],
            'inventory_size': 3,
        }
        component = FakeComponent(self.manager, data)
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

        class FakeComponent(Component):
            schema = fakeschema
            clean_inventory = Mock(
                __name__='clean_inventory', return_value=True
            )
            clean_inventory_size = Mock(
                __name__='clean_inventory_size', return_value=True
            )

        data = {
            'inventory': [1, 2],
            'inventory_size': 2,
        }
        player = FakeComponent(self.manager)
        player.is_valid(data)
        player.schema.find_errors.assert_called_once_with(data)
        player.clean_inventory.assert_called_once_with([1, 2])
        player.clean_inventory_size.assert_called_once_with(2)

    def test_is_valid_field_invalid(self):
        class FakeComponent(Component):
            clean_inventory = Mock(
                __name__='clean_inventory', return_value=False
            )

        data = {
            'inventory': [1, 2],
            'inventory_size': 2,
        }
        player = FakeComponent(self.manager)
        valid = player.is_valid(data)
        self.assertFalse(valid)
        self.assertEqual(player.errors, ['inventory was not valid'])
        FakeComponent.clean_inventory.assert_called_once_with(
            data['inventory']
        )

    def test_is_valid_clean_False(self):
        class FakeComponent(Component):
            clean = Mock(return_value=False)

        data = {
            'inventory': [1, 2],
        }
        player = FakeComponent(self.manager)
        valid = player.is_valid(data)
        self.assertFalse(valid)
        self.assertEqual(player.errors, ['{0} did not validate'.format(data)])

    @patch('yape.manager.Manager.get_font')
    @patch('yape.manager.Manager.get_sprite')
    @patch('yape.manager.Manager.get_image')
    @patch('yape.manager.Manager.get_json')
    def test_process_auto_fields(self, mock_json, mock_image, mock_sprite,
        mock_font):
        data = {
            'inventory': [], 'inventory_size': 0,
            'image': 'image',
            'sprite': ['sprite_filename', 0, 0],
            'font': ('font', 16),
            'json': ('path', 'filename'),
        }
        PlayerComponent.image_fields = ['image']
        PlayerComponent.sprite_fields = {'sprite': (32, 32)}
        PlayerComponent.font_fields = ['font']
        PlayerComponent.json_fields = ['json']
        PlayerComponent(self.manager, data)
        mock_image.assert_called_once_with('image')
        mock_sprite.assert_called_once_with('sprite_filename', 0, 0, 32, 32)
        mock_font.assert_called_once_with('font', 16)
        mock_json.assert_called_once_with('path', 'filename')


class MapComponent(LoadableComponent):
    path = 'test_path'


class LoadableComponentTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = Manager(self.path)

    @patch('yape.components.LoadableComponent.load_location')
    def test_init(self, mock_load_location):
        data = {'a': 1}
        mock_load_location.return_value = data
        MapComponent(self.manager)
        self.assertFalse(mock_load_location.called)
        game_map_b = MapComponent(self.manager, 'test_location.json')
        mock_load_location.assert_called_once_with('test_location.json')
        self.assertEqual(game_map_b.a, data['a'])

    @patch('yape.manager.Manager.get_json')
    def test_load_location(self, mock_get_json):
        data = {'a': 1}
        mock_get_json.return_value = data
        game_map = MapComponent(self.manager, 'test_location.json')
        mock_get_json.assert_called_once_with(self.path, 'test_location.json')
        self.assertEqual(game_map.a, data['a'])
