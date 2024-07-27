import sqlite3 as sq
import config

def db_connect():
    db = sq.connect(config.path_to_db)
    return db


def add_warn(user_id, user_name, reason):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warns (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USER_ID INTEGER,
    USER_NAME TEXT,
    REASON TEXT
    )
    """)

    cursor.close()
    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO warns (USER_ID, USER_NAME, REASON) VALUES (?, ?, ?);
    """, (user_id, user_name, reason))
    db.commit()
    cursor.close()
    db.close()
    return "Выполнено!"


def delete_warn(ids):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute("""
    DELETE FROM warns WHERE ID = ?
    """, (ids, ))
    db.commit()
    cursor.close()
    db.close()
    return 'Удалено!'


def all_user_warn(nick):
    db = db_connect()
    cursor = db.cursor()
    cursor.execute("""
    SELECT * FROM warns
    WHERE USER_ID = ?
    """, (nick, ))
    sstring = ""
    for i in cursor:
        str_warn = " "
        for o in i:
            str_warn += str(o)
            str_warn += " "
        sstring += f"{str_warn}\n"
    cursor.close()
    db.close()
    return sstring


def get_count_warn():
    db = db_connect()
    cursor = db.cursor()
    cursor.execute(
    """
    SELECT USER_ID, COUNT(*) FROM WARNS
    GROUP BY USER_ID
    """)
    liste = []
    for i in cursor:
        liste.append(i)
    return liste

def counter(count):
    if count <= 10:
        return 100
    elif count <= 15:
        return 105
    elif count > 15:
        return 200
# 100 - 20 minutes
# 105 - 6 hour
# 200 - ban

