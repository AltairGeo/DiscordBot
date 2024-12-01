import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
from config import colorscheme
import db
from asyncio import AbstractEventLoop


hist = db.db()

async def db_connect(loop: AbstractEventLoop):
    conn = await hist.conn_create(loop=loop)
    return conn

async def db_hist_init(loop) -> None:
    db = await db_connect(loop=loop)
    cur = await db.cursor()
    await cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        ID INT PRIMARY KEY AUTO_INCREMENT,
        AUTHOR TEXT,
        AUTHOR_ID TEXT,
        CONTENT TEXT,
        CHANNEL TEXT,
        CHANNEL_ID TEXT,
        TIME TEXT,
        ACTION TEXT
                )
    """)
    await cur.close()


async def get_count_hist_for_mouth(mounth: int, year: int, loop: AbstractEventLoop):
    db = await db_connect(loop=loop)
    cursor = await db.cursor() # Подключение к бд

    await cursor.execute("""
    SELECT 
        DATE_FORMAT(TIME, '%%Y-%%m-%%d') AS DAY,
        COUNT(*) AS COUNT
    FROM 
        history
    WHERE 
        STR_TO_DATE(TIME, '%%Y-%%m-%%d') LIKE %s AND ACTION = 'WRITE'
    GROUP BY 
        DATE_FORMAT(TIME, '%%Y-%%m-%%d')
    ORDER BY 
        DAY;
""", (f'{year:04d}-{mounth:02d}-%',)) # Запрос к бд

    data = await cursor.fetchall()
    if data == []:
        return None
    datas = []
    counts = []
    for i in data:
        datas.append(datetime.datetime.fromisoformat(i[0]))
        counts.append(i[1])
    buf = BytesIO()
    plt.figure(figsize=(8.0, 4.0))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.plot(datas, counts, color=colorscheme[2], marker='.', markersize=7)
    plt.xlabel('Месяц-День')
    plt.ylabel('Количество сообщений')
    plt.title('Количество сообщений за месяц по дням')
    plt.gcf().autofmt_xdate()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await cursor.close()
    plt.close()
    return buf


# Круговая диограмма. Распределение сообщений по каналам сервера
async def get_channels_statistic(mounth: int, year: int, loop: AbstractEventLoop):
    conn = await db_connect(loop=loop)
    cursor = await conn.cursor() # Подключение к бд

    await cursor.execute("""
    SELECT 
        CHANNEL,
        COUNT(*) AS COUNT
    FROM 
        history
    WHERE 
        DATE_FORMAT(TIME, '%%Y-%%m') = %s AND ACTION = 'WRITE'
    GROUP BY 
        CHANNEL
    ORDER BY 
        COUNT DESC;
    """, (f'{year}-{mounth:02d}',))
    

    data = await cursor.fetchall()
    await cursor.close()
    labels = []
    counts = []
    for i in data:
        labels.append(i[0])
        counts.append(i[1])
    explodee = []
    for i in range(len(labels)):
        if i == 0:
            explodee.append(0.05)
        else:
            explodee.append(0)
    plt.figure(figsize=(7, 4))
    plt.pie(counts, labels=labels, explode=explodee, colors=colorscheme)
    plt.title(f"Распределение сообщений по каналам сервера за {year}-{mounth}")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


# Круговая диограмма статистики по авторам
async def get_author_stat(mounth: int, year: int, loop: AbstractEventLoop):
    conn = await db_connect(loop=loop)
    cursor = await conn.cursor() # Подключение к бд

    await cursor.execute("""
    SELECT 
        AUTHOR,
        COUNT(*) AS COUNT
    FROM 
        history
    WHERE 
        DATE_FORMAT(TIME, '%%Y-%%m') = %s AND ACTION = 'WRITE'
    GROUP BY 
        AUTHOR
    ORDER BY 
        COUNT DESC;
    """, (f'{year}-{mounth:02d}',))
    
    
    data = await cursor.fetchall()
    labels = []
    counts = []
    for i in data:
        labels.append(i[0])
        counts.append(i[1])
    
    count_all_messages = sum(counts)

    data_sorted = sorted(zip(counts, labels), reverse=True)
    top_6 = data_sorted[:6]
    labels = []
    counts = []
    for i in top_6:
        labels.append(i[1])
        counts.append(i[0])
    # Вычисляем других    
    count_top6_message = sum(counts)
    others = count_all_messages - count_top6_message
    # добавляем других
    labels.append("Остальные")
    counts.append(others)
    explodee = []
    for i in range(len(labels)):
        if i == 0:
            explodee.append(0.07)
        else:
            explodee.append(0)
    plt.figure(figsize=(10, 6)) 
    plt.pie(counts, labels=labels, explode=explodee, autopct='%1.f%%', colors=colorscheme)
    plt.legend(labels, loc='upper right', bbox_to_anchor=(1.3, 1))
    plt.title(f"Распределение сообщений по участникам за {year}-{mounth}")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    await cursor.close()
    return buf