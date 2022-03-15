from typing import Union, List, Callable, Optional, Iterable, Any
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


class SelectableList:
    def __init__(self, items: Iterable[Any],
                 title: str = '',
                 item_show_cb: Optional[Callable[[Any], str]] = None):
        if len(items) == 0:
            raise ValueError('iterable is empty')
        self._items = items
        self._gui_items = []
        self._selected = 0
        self._title = title
        if item_show_cb is not None:
            self._item_show_cb = item_show_cb
        else:
            self._item_show_cb = lambda x: str(x)

    def create(self):
        with dpg.group():
            dpg.add_text(self._title)
            for i, item in enumerate(self._items):
                item_label = self._item_show_cb(item)
                gui_item = dpg.add_text(item_label)
                self._gui_items.append(gui_item)
        self.select_other(0)

    def select_other(self, inc: int):
        old_selected = self._selected
        label_for_old = self._item_show_cb(self._items[old_selected])

        new_selected = self._selected + inc
        if new_selected < 0:
            new_selected = 0
        if new_selected > len(self._items):
            new_selected = len(self._items)

        label_for_new = '-> ' + self._item_show_cb(self._items[new_selected])

        dpg.set_value(self._gui_items[old_selected], label_for_old)
        dpg.set_value(self._gui_items[new_selected], label_for_new)
        self._selected = new_selected

    def get_selected(self):
        return self._item_show_cb(self._items[self._selected])