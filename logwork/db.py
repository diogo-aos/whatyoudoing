def exists_table(con, name):
    cur = con.execute('''SELECT name FROM sqlite_master
                         WHERE type='table' AND name='{}';'''.format(name))
    return len(cur.fetchall()) > 0

def create_tables(con):
    if not exists_table(con, 'task'):
        con.execute('''CREATE TABLE task
                     (id INTEGER PRIMARY KEY,
                      start TIMESTAMP,
                      end TIMESTAMP,
                      name_id INTEGER,
                      comments TEXT,
                      chain_backward INTEGER,
                      chain_forward INTEGER,
                      FOREIGN KEY(name_id) REFERENCES task_name(id)
                      FOREIGN KEY(chain_backward) REFERENCES task(id),
                      FOREIGN KEY(chain_forward) REFERENCES task(id))''')

    if not exists_table(con, 'window'):
        con.execute('''CREATE TABLE window
                     (id INTEGER PRIMARY KEY,
                      ts TIMESTAMP,
                      name TEXT,
                      task_id INTEGER,
                      FOREIGN KEY(task_id) REFERENCES task(id))''')

    if not exists_table(con, 'task_name'):
        con.execute('''CREATE TABLE task_name
                     (id INTEGER PRIMARY KEY,
                      name TEXT)''')
    con.commit()
