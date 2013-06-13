import os
import json
from StringIO import StringIO

from unittest import TestCase

from mock import Mock, MagicMock, call, patch

from yape.manager import (GenericAssetManager, ImageManager, FontManager,
    SpriteManager, JSONManager, Manager, JSONList)


class FakeRect(object):

    def __init__(self, **kwargs):
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)
        self.width = kwargs.get('width', 320)
        self.height = kwargs.get('height', 320)

    def __setattr__(self, key, value):
        if all(map(
            lambda attr: hasattr(self, attr), ['x', 'y', 'width', 'height']
        )):
            if ((key == 'x' and value > self.x + self.width) or
                (key == 'y' and value > self.y + self.height)):
                raise ValueError()
        super(FakeRect, self).__setattr__(key, value)


class FakeImage(object):

    def __init__(self, image, **kwargs):
        self.rect = FakeRect(**kwargs)
        self.image = image

    def get_rect(self):
        return self.rect

    def subsurface(self, rect):
        self.rect = rect
        return self


class GenericAssetManagerTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = GenericAssetManager(self.path)

    @patch('yape.manager.GenericAssetManager._load_asset')
    def test_get_cache_empty(self, mock_load_asset):
        value = self.manager.get('key')
        self.assertTrue(mock_load_asset.called)

    @patch('yape.manager.GenericAssetManager._load_asset')
    def test_get_cache_present(self, mock_load_asset):
        expected_value = JSONList(['value'])
        self.manager.cache[('key',)] = expected_value
        value = self.manager.get('key')
        self.assertEqual(value, expected_value)
        self.assertFalse(mock_load_asset.called)

    @patch('yape.manager.GenericAssetManager.load')
    def test_load_asset_failed(self, mock_load):
        expected_value = JSONList(['value'])
        mock_load.return_value = expected_value
        mock_load.side_effect = Exception
        value = self.manager.get('key')
        self.assertEqual(value, None)
        self.assertTrue(mock_load.called)

    @patch('yape.manager.GenericAssetManager.load')
    def test_load_asset_asset_none_not_stored(self, mock_load):
        expected_value = None
        mock_load.return_value = expected_value
        value = self.manager.get('key')
        self.assertEqual(value, expected_value)
        self.assertTrue(mock_load.called)

    @patch('yape.manager.GenericAssetManager.load')
    def test_load_asset_asset_stored(self, mock_load):
        expected_value = JSONList(['value'])
        mock_load.return_value = expected_value
        value = self.manager.get('key')
        self.assertEqual(value, expected_value)
        self.assertTrue(mock_load.called)
        self.assertEqual(self.manager.cache[('key',)], expected_value)


class ImageManagerTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = ImageManager(self.path)

    def test_image_load(self):
        with patch('pygame.image.load') as mock_pygame_image_load:
            mock_pygame_image_load.return_value = MagicMock()
            filename = 'image1'
            image = self.manager.get(filename)
            expected_path = os.path.join(self.path, filename)
            self.assertEqual(
                mock_pygame_image_load.call_args, call(expected_path)
            )
            self.assertEqual(
                self.manager.cache[(filename,)], image
            )


class SpriteManagerTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = SpriteManager(self.path)

    @patch('yape.manager.ImageManager.get')
    def test_sprite_load_failed_image(self, mock_image_get):
        mock_image_get.return_value = None
        sprite = self.manager.get('image1', 0, 0, 32, 32)
        self.assertEqual(sprite, None)
        self.assertEqual(mock_image_get.call_args, call('image1',))

    @patch('yape.manager.ImageManager.load')
    def test_spirte_load_caches_image(self, mock_image_load):
        mock_image = FakeImage(image=b'0')
        mock_image_load.return_value = mock_image
        sprite_1 = self.manager.get('image1', 0, 0, 32, 32)
        sprite_2 = self.manager.get('image1', 32, 32, 32, 32)
        sprite_3 = self.manager.get('image2', 0, 0, 32, 32)
        # The two unique images should be in the image cache
        # They should only be loaded once each
        expected_image_cache_keys = [
            ('image1',), ('image2',)
        ]
        expected_image_load_calls = [
            call('image1',), call('image2',),
        ]
        self.assertEqual(
            self.manager.image_manager.cache.keys(), expected_image_cache_keys
        )
        self.assertEqual(
            mock_image_load.call_args_list, expected_image_load_calls,
            'Only one load call should occur for each image'
        )

    @patch('yape.manager.ImageManager.load')
    def test_sprite_load_bad_rect(self, mock_image_load):
        mock_image = FakeImage(image=b'0', width=64, height=64)
        mock_image_load.return_value = mock_image
        sprite_1 = self.manager.get('image1', 64, 64, 32, 32)
        self.assertEqual(sprite_1.rect.x, 64)
        self.assertEqual(sprite_1.rect.y, 64)
        self.assertEqual(sprite_1.rect.width, 32)
        self.assertEqual(sprite_1.rect.height, 32)

    @patch('yape.manager.ImageManager.load')
    def test_sprite_load_valid(self, mock_image_load):
        mock_image = FakeImage(image=b'0')
        mock_image_load.return_value = mock_image
        sprite_1 = self.manager.get('image1', 64, 64, 32, 32)
        self.assertEqual(sprite_1.rect.x, 64)
        self.assertEqual(sprite_1.rect.y, 64)
        self.assertEqual(sprite_1.rect.width, 32)
        self.assertEqual(sprite_1.rect.height, 32)


class FontManagerTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = FontManager(self.path)

    @patch('pygame.font.Font')
    def test_font_load(self, mock_pygame_font):
        mock_pygame_font.return_value = MagicMock()
        filename = 'font1'
        font = self.manager.get(filename, 12)
        expected_path = os.path.join(self.path, filename)
        self.assertEqual(
            mock_pygame_font.call_args, call(expected_path, 12)
        )
        self.assertEqual(
            self.manager.cache[(filename, 12)], font
        )


@patch('__builtin__.open')
class JSONManagerTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = JSONManager(self.path)

    def test_load_filename_path(self, mock_open):
        mock_open.return_value = StringIO()
        json_data = self.manager.load('maps', 'map_1')
        expected_path = os.path.join(self.path, 'maps', 'map_1')
        self.assertEqual(mock_open.call_args, call(expected_path))

    def test_load_no_file(self, mock_open):
        mock_open.side_effect = IOError
        json_data = self.manager.load('maps', 'map_1')
        self.assertEqual(json_data, None)

    def test_load_empty_file(self, mock_open):
        mock_open.return_value = StringIO()
        json_data = self.manager.load('maps', 'map_1')
        self.assertEqual(json_data, None)

    def test_load_invalid_json(self, mock_open):
        file_contents = '{"key": "value", "bad,syntax4"}'
        mock_open.return_value = StringIO(file_contents)
        json_data = self.manager.load('maps', 'map_1')
        self.assertEqual(json_data, None)

    def test_json_with_dict(self, mock_open):
        file_data = {
            'key1': 'value1',
            'key2': 'value2',
        }
        file_contents = json.dumps(file_data)
        mock_open.return_value = StringIO(file_contents)
        json_data = self.manager.load('maps', 'map_1')
        self.assertEqual(json_data, file_data)

    def test_json_with_list(self, mock_open):
        file_data = [
            {
                'key': 'value',
            },
            {
                'key': 'value',
            },
        ]
        file_contents = json.dumps(file_data)
        mock_open.return_value = StringIO(file_contents)
        json_data = self.manager.load('maps', 'map_1')
        self.assertEqual(json_data, file_data)


class ManagerTestCase(TestCase):

    def setUp(self):
        self.path = 'test_path'
        self.manager = Manager(self.path)

    def test_paths(self):
        expected_path = self.path
        expected_image_path = os.path.join(self.path, 'images')
        expected_font_path = os.path.join(self.path, 'fonts')
        self.assertEqual(self.manager._json_manager.path, expected_path)
        self.assertEqual(self.manager._image_manager.path, expected_image_path)
        self.assertEqual(self.manager._sprite_manager.path, expected_image_path)
        self.assertEqual(self.manager._font_manager.path, expected_font_path)

    @patch('yape.manager.JSONManager.get')
    def test_get_json(self, mock_json_get):
        mock_json_get.return_value = {}
        json_data = self.manager.get_json('map', 'map_1')
        self.assertEqual(json_data, {})
        self.assertEqual(mock_json_get.call_args, call('map', 'map_1'))

    @patch('yape.manager.ImageManager.get')
    def test_get_image(self, mock_image_get):
        mock_image_get.return_value = ''
        image_data = self.manager.get_image('image1')
        self.assertEqual(image_data, '')
        self.assertEqual(mock_image_get.call_args, call('image1'))

    @patch('yape.manager.FontManager.get')
    def test_get_font(self, mock_font_get):
        mock_font_get.return_value = ''
        # fontsize defaults to 16 if not provided
        font_data = self.manager.get_font('font1')
        self.assertEqual(font_data, '')
        self.assertEqual(mock_font_get.call_args, call('font1', 16))
        # assure provided fontsize is passed
        font_data = self.manager.get_font('font1', 12)
        self.assertEqual(font_data, '')
        self.assertEqual(mock_font_get.call_args, call('font1', 12))

    @patch('yape.manager.SpriteManager.get')
    def test_get_sprite(self, mock_sprite_get):
        mock_sprite_get.return_value = ''
        sprite_data = self.manager.get_sprite('sprite1', 0, 0, 32, 32)
        self.assertEqual(sprite_data, '')
        self.assertEqual(
            mock_sprite_get.call_args, call('sprite1', 0, 0, 32, 32)
        )

