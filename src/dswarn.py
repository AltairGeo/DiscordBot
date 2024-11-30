import sqlite3 as sq
from db import db
 
warns = db()

async def db_connect(loop):
    conn = await warns.conn_create(loop=loop)
    return conn

async def add_warn(user_id, user_name, reason, loop):
    try:
        conn = await db_connect(loop=loop)
        cursor = await conn.cursor()
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS warns (
        ID INT PRIMARY KEY AUTO_INCREMENT,
        USER_ID TEXT,
        USER_NAME TEXT,
        REASON TEXT
        );
        """)
        await cursor.close()
        cursor = await conn.cursor()
        await cursor.execute("""
        INSERT INTO warns (USER_ID, USER_NAME, REASON) VALUES (%s, %s, %s);
        """, (int(user_id), user_name, reason))
        await conn.commit()
        await cursor.close()
        return f"Выдано предупреждение пользователю {user_name}"
    except Exception as e:
        return f"Ошибка: {e}"

async def delete_warn(ids, loop):
    try:
        conn = await db_connect(loop=loop)
        cursor = await conn.cursor()
        await cursor.execute("""
        DELETE FROM warns WHERE ID = %s
        """, (ids, ))
        await conn.commit()
        await cursor.close()
        return 'Удалено!'
    except Exception as e:
        return f"Ошибка: {e}"
        


async def all_user_warn(user_id, loop):
    try:
        db = await db_connect(loop)
        cursor = await db.cursor()
        await cursor.execute("""
        SELECT * FROM warns
        WHERE USER_ID = %s
        """, (user_id, ))
        resp = []
        for i in await cursor.fetchall():
            resp.append(i)
        
        return resp
    except Exception as e:
        return f"Ошибка: {e}"

async def get_count_warn(loop):
    try:
        db = await db_connect(loop)
        cursor = await db.cursor()
        await cursor.execute(
        """
        SELECT USER_ID, COUNT(*) FROM warns
        GROUP BY USER_ID
        """)
        liste = []
        for i in await cursor.fetchall():
            liste.append(i)
        return liste
    except Exception as e:
        return f"Ошибка: {e}"

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


async def warn_system(ids, loop):
    list_of_warns = await get_count_warn(loop)
    for i in list_of_warns:
        if int(i[0]) == ids:
            result = counter(i[1])
            return result

