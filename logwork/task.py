from subprocess import Popen, PIPE
from datetime import datetime
import sqlite3

class Task:
    def __init__(self, name, db_path):
        self.name = name
        self.db_path = db_path
        self.db_con = sqlite3.connect(db_path)

        self.comment = None
        self.chain_forward = None
        self.chain_backward = None

        self._last_windowname = ''

    def start(self):
        self.ts_start = datetime.now()

        cur = self.db_con.execute('''INSERT INTO task_name(name)
                                     VALUES (?)''',
                                  (self.name,))
        self.name_id = cur.lastrowid

        cur = self.db_con.execute('''INSERT INTO task(start, end, name_id, comments, chain_backward, chain_forward)
                                     VALUES (?,?,?,?,?,?)''',
                                  (self.ts_start, None, self.name_id, self.comment, self.chain_backward, self.chain_forward))
        self.task_id = cur.lastrowid

        # chain previous task to self
        if self.chain_backward is not None:
            self.db_con.execute('''UPDATE task SET chain_forward=? WHERE id=?''',
                        (self.task_id, self.chain_backward))

        self.db_con.commit()

    def store_window(self):
        name = get_active_window_name()
        # insert new window if different than previous
        if name != self._last_windowname:
            self.db_con.execute('''INSERT INTO window(ts, name, task_id)
                              VALUES (?,?,?)''', (datetime.now(), name, self.task_id))
            self.db_con.commit()
            self._last_windowname = name

    def pause(self):
        self.end()
        self.db_con.execute('''UPDATE task SET end=? WHERE id=?''',
                    (self.ts_end, self.task_id))
        self.db_con.commit()
        self.db_con.close()

        new_task = Task(self.name, self.db_path)
        self.chain_backward = self.task_id

        return new_task


    def end(self):
        self.ts_end = datetime.now()

    def commit(self, comment):
        self.comment = comment
        self.db_con.execute('''UPDATE task SET end=?, comments=? WHERE id=?''',
                    (self.ts_end, comment, self.task_id))
        self.db_con.commit()
        self.db_con.close()

def get_active_window_name():
    windowname = Popen(['xdotool', 'getactivewindow'],  stdout=PIPE)
    windowname.wait()
    try:
        window_num = int(windowname.stdout.read())
    except:
        return None
    name = Popen(['xdotool', 'getwindowname', str(window_num)],  stdout=PIPE)
    name.wait()
    return name.stdout.read().decode('utf-8')
