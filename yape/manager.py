import os
import json
from weakref import WeakValueDictionary

from yape.types import JSONDict, JSONList

import pygame


class GenericAssetManager(object):

    def __init__(self, path):
        self.path = path
        self.cache = WeakValueDictionary()

    def _load_asset(self, *args):
        try:
            asset = self.load(*args)
        except Exception as e:
            asset = None
            print "Error {0} while loading {1}".format(e, args)
        else:
            if asset is not None:
                self.cache[args] = asset
        return asset

    def load(self, *args):
        raise NotImplementedError('Must be implemented by a subclass')

    def get(self, *args):
        try:
            asset = self.cache[args]
        except KeyError:
            asset = self._load_asset(*args)
        return asset


class FontManager(GenericAssetManager):

    def load(self, filename, font_size):
        filename = os.path.join(self.path, filename)
        return pygame.font.Font(filename, font_size)


class ImageManager(GenericAssetManager):

    def load(self, filename):
        filename = os.path.join(self.path, filename)
        return pygame.image.load(filename).convert_alpha()


class SpriteManager(GenericAssetManager):

    def __init__(self, path):
        super(SpriteManager, self).__init__(path)
        self.image_manager = ImageManager(path)

    def load(self, filename, x_offset, y_offset, width, height):
        image = self.image_manager.get(filename)
        if image is None:
            return None
        rect = image.get_rect()
        try:
            rect.x, rect.y = x_offset, y_offset
            rect.width, rect.height = width, height
        except ValueError:
            err_msg = 'Spritesheet with filename {filename} cannot load a sprite at {x},{y} with dimensions {width}x{height}'
            print err_msg.format(
                filename=filename, x=x_offset, y=y_offset, width=width,
                height=height
            )
        else:
            image = image.subsurface(rect)
        return image


class JSONManager(GenericAssetManager):

    def _load_file_data(self, filename):
        try:
            f = open(filename)
            contents = f.read()
        except IOError:
            contents = None
            print 'Could not open JSON file {0}'.format(filename)
        return contents

    def load(self, filename):
        full_filename = os.path.join(self.path, filename)
        file_contents = self._load_file_data(full_filename)
        if file_contents is None:
            return None
        try:
            json_data = json.loads(file_contents)
        except ValueError as e:
            print 'Invalid JSON in file {0}. {1}'.format(full_filename, e)
            return None
        kls = JSONDict if isinstance(json_data, dict) else JSONList
        return kls(json_data)


class Manager(object):
    """
    Client class for obtaining and cacheing unique references to assets from
    the filesystem. Uses weak references to hold a unique object in memory
    while used and free it once it is no longer in use.
    """

    def __init__(self, assets_dir):
        self.path = assets_dir
        images_dir = os.path.join(assets_dir, 'images')
        fonts_dir = os.path.join(assets_dir, 'fonts')
        self._json_manager = JSONManager(assets_dir)
        self._image_manager = ImageManager(images_dir)
        self._sprite_manager = SpriteManager(images_dir)
        self._font_manager = FontManager(fonts_dir)

    def get_json(self, sub_path, filename):
        filename = os.path.join(sub_path, filename)
        return self._json_manager.get(filename)

    def get_image(self, filename):
        return self._image_manager.get(filename)

    def get_sprite(self, filename, x, y, width, height):
        return self._sprite_manager.get(filename, x, y, width, height)

    def get_font(self, filename, font_size=16):
        return self._font_manager.get(filename, font_size)

