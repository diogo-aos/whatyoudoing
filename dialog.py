import sys
import datetime
import logging
import os
from collections import deque
from typing import List
import pathlib

import appdirs
import dearpygui.dearpygui as dpg

from gui_utils import KeyDown

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
    log_line =  f'{datetime.datetime.now()} | {text}'
    print(log_line)
    with open(db_path, 'a+') as f:
        f.write(log_line + '\n')
    sys.exit(1)


def enter_cb():
    if lctrl_key.is_down:
        logger.debug("ctrl enter")
        save_cb()

lctrl_key = KeyDown(341)  # 341 == left control, 345 == right control
enter_key = KeyDown(257, release_callback=enter_cb)  # carriege return = 257


# keyboard registry
with dpg.handler_registry():
    lctrl_key.register()
    enter_key.register()


with dpg.window(label="What were you doing?", tag='First'):
    dpg.add_text(f'Now: {datetime.datetime.now()}')

    last_entries = get_last_n_entries(5)
    dpg.add_text(f'Last {len(last_entries)} entries:')
    for e in last_entries:
        dpg.add_text(e)

    default_value = last_entries[-1].split('| ')[-1] if len(last_entries) > 0 else ""
    dpg.add_input_text(tag='user_text',
                       hint="What were you doing?",
                       multiline=True,
                       default_value=default_value
    )
    dpg.add_button(label="Save", callback=save_cb)

dpg.create_viewport(title='What were you doing?', width=600, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window('First', True)
dpg.start_dearpygui()

dpg.destroy_context()
