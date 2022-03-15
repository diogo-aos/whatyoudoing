import sys
import datetime
import logging
import os
from collections import deque
from typing import List
import pathlib

import appdirs
import dearpygui.dearpygui as dpg

from gui_utils import KeyDown, SelectableList

logger = logging.getLogger('dialog')

db_filename = 'log.txt'

user_data_dir = appdirs.user_data_dir('whatyoudoing')
db_path = os.path.join(user_data_dir, db_filename)

if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)  # create user app data directories

dpg.create_context()


def get_last_n_entries(n: int = 5, path: str = db_path) -> List[str]:
    if not os.path.exists(path):
        return []

    d = deque(maxlen=n)
    with open(path, 'r') as f:
        for line in f:
            d.append(line.strip())
    return list(d)


def save_cb():
    text = dpg.get_value('user_text').replace('\n', '; ')
    log_line = f'{datetime.datetime.now()} | {text}'
    print(log_line)
    with open(db_path, 'a+') as f:
        f.write(log_line + '\n')
    sys.exit(1)


def enter_cb():
    if lctrl_key.is_down:
        logger.debug("ctrl enter")
        save_cb()


def which_key(sender, x, y):
    print(sender, x, y)


# 340 - left shift
# 344 - right shift
# 264 - down arrow
# 265 - up arrow


def rm_task_timestamp(t):
    return t.split('| ')[-1]


def get_timstamp(t):
    return t.split('| ')[0]


with dpg.window(label="What were you doing?", tag='First'):
    dpg.add_text(f'Now: {datetime.datetime.now()}')

    last_entries = get_last_n_entries(20)
    entry_list = SelectableList(items=last_entries[::-1], title='Last entries:', item_show_cb=rm_task_timestamp)
    default_value = rm_task_timestamp(last_entries[-1]) if len(last_entries) > 0 else ""

    dpg.add_text(f'Last entry time: {get_timstamp(last_entries[-1])}')

    with dpg.group(horizontal=True):
        with dpg.group(horizontal=False):
            input_area = dpg.add_input_text(tag='user_text',
                                            hint="What were you doing?",
                                            multiline=True,
                                            )
            dpg.add_button(label="Save", callback=save_cb)
        with dpg.group(horizontal=False):
            entry_list.create()

    def change_up_down(inc):
        if lctrl_key.is_down:
            entry_list.select_other(inc)

    def copy_to_input():
        if lctrl_key.is_down:
            val = dpg.get_value(input_area)
            added_val = entry_list.get_selected()
            print('left arrow', val, added_val)
            new_val = f'{val}\n{added_val}'.strip()
            dpg.set_value(input_area, new_val)

    lctrl_key = KeyDown(341)  # 341 == left control, 345 == right control
    enter_key = KeyDown(257, release_callback=enter_cb)  # carriege return = 257

    down_key = KeyDown(264, release_callback=lambda: change_up_down(1))  # down
    up_key = KeyDown(265, release_callback=lambda: change_up_down(-1))  # up
    left_key = KeyDown(263, release_callback=copy_to_input)  # left

    # keyboard registry
    with dpg.handler_registry():
        lctrl_key.register()
        enter_key.register()
        down_key.register()
        up_key.register()
        left_key.register()
        #dpg.add_key_press_handler(callback=which_key)

dpg.create_viewport(title='What were you doing?', width=600, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window('First', True)
dpg.start_dearpygui()

dpg.destroy_context()
