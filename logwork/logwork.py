from datetime import datetime
import sqlite3
import curses
from curses.textpad import Textbox, rectangle
import time
from os.path import expanduser, join

from db import *
from task import Task


def main(stdscr):
    PERIOD = 0.25
    # task_name = input('task name:')
    # print('task started at {}'.format(datetime.now()))

    stdscr.clear()  # clear screen
    stdscr.addstr(0,0, "Task name:")
    curses.echo()
    task_name = stdscr.getstr(1,0,30)
    curses.noecho()

    # db_path = join(expanduser('~'),'.task_db.sqlite3')
    db_path = 'test.sqlite3'

    con = sqlite3.connect(db_path)
    create_tables(con)
    con.close()

    task = Task(task_name, db_path)
    task.start()

    stdscr.clear()  # clear screen
    stdscr.addstr(0,0, "Task: {}".format(task.name))
    stdscr.addstr(1,0, "Started: {}".format(task.ts_start))
    stdscr.addstr(2,0, "Elapsed: ")
    stdscr.addstr(3,0, "f(finish) p(pause/resume)\n")

    paused = False
    exec_ic = True

    stdscr.nodelay(True)
    while True:
        time.sleep(PERIOD)
        if not paused:
            if exec_ic:
                stdscr.addstr(5,0, "\ \n")
                exec_ic = False
            else:
                stdscr.addstr(5,0, "/ \n")
                exec_ic = True
            task.store_window()
            ts_dif = datetime.now() - task.ts_start
            stdscr.addstr(2,0, "Elapsed: {}".format(str(ts_dif).split('.')[0]))
        # stdscr.refresh()
        c = stdscr.getch()

        if c == ord('p'):
            if not paused:
                stdscr.addstr(5,0, "p\n")
                paused = True
                task = task.pause()  # pause returns new task
            else:
                task.start()
                stdscr.addstr(1,0, "Started: {}".format(task.ts_start))
                paused = False
        if c == ord('f'):
            task.end()
            break

    stdscr.nodelay(False)
    stdscr.clear()  # clear screen
    stdscr.addstr(0,0, "Task: {}".format(task.name))
    stdscr.addstr(1,0, "Insert comments (Ctrl-G to finish editing):")

    edit_h, edit_w = 5, 30
    edit_y, edit_x = 3, 1
    editwin = curses.newwin(edit_h, edit_w, edit_y, edit_x)
    rect_y, rect_x = edit_y - 1, edit_x - 1
    rect_h, rect_w = 1 + edit_h + 2, 1 + edit_w + 1
    rectangle(stdscr, rect_y, rect_x, rect_h, rect_w)
    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()
    stdscr.clear()  # clear screen
    stdscr.addstr(0,0, "finished (press enter to exit)".format(len(message)))

    while True:
        time.sleep(0.1)
        c = stdscr.getkey()

        if c == '\n':
            break

curses.wrapper(main)
