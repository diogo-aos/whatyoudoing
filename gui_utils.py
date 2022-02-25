from typing import Union, List, Callable, Optional
import logging

import dearpygui.dearpygui as dpg

logger = logging.getLogger('gui_utils')


class KeyDown:
    def __init__(self, key: int,
                 down_callback: Optional[Callable] = None,
                 release_callback: Optional[Callable] = None):
        self.key = key
        self.is_down = False
        self.down_cb = down_callback
        self.release_cb = release_callback

    def register(self, ):
        dpg.add_key_down_handler(key=self.key, callback=self.key_cb, user_data='down')
        dpg.add_key_release_handler(key=self.key, callback=self.key_cb, user_data='release')

    def key_cb(self, sender, app_data, user_data):
        logger.debug(self.key, user_data)
        key_was_down = self.is_down
        key_is_down = user_data == 'down'
        self.is_down = key_is_down

        if self.down_cb is not None and \
                key_is_down and not key_was_down:
            self.down_cb()
        if self.release_cb is not None and not key_is_down:
            logger.debug('calling release cb')
            self.release_cb()


class MultiKeyDown:
    def __init__(self, keys: List[int], callback: Optional[Callable]):
        self.keys = {}
        for k in keys:
            self.keys[k] = KeyDown(k)

        self.n_keys = len(keys)
        self.n_down = 00

    def inc_down(self):
        self.n_down += 1

    def dec_down(self):
        self.n_down -= 1

    def combination_down(self):
        self.n_keys == self.n_down

    def add_key_to_tag(self, key:int, tag: str):
        if tag not in self.tags:
            self.tags[tag] = []
            self.tag_down[tag] = 0

        self.tags[tag].append(key)

    def is_tag_down(self, tag):
        return self.tags[tag] > 1

    def register_key(self, key: Union[int, List[int]], tag: str, callback: Optional[Callable] = None):
        if isinstance(key, int):
            key = [key]

        for k in key:
            if k in self.keys:
                raise Exception(f'key {k} already registered with tag {self.keys[k]}')

            self.keys[k] = tag
            self.key_down[k] = False
            self.add_key_to_tag(k, tag)

            dpg.add_key_down_handler(key=k, callback=self.key_down_cb, user_data='down')
            dpg.add_key_release_handler(key=k, callback=self.key_down_cb, user_data='release')

    def key_down_cb(self, k, app_data, user_data):
        key_was_down = self.key_down[k]
        key_is_down = user_data == 'down'

        self.key_down[k] = key_is_down  # update current state of key

        if key_is_down:
            if not key_was_down:  # if key was not down before, update its tag
                self.tags[self.keys[k]] += 1
        else:  # key was released
            self.tags[self.keys[k]] -= 1




class KeyCombination:
    def __init__(self):
        pass