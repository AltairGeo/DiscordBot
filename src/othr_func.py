from bs4 import BeautifulSoup
import config, random
import sqlite3 as sq
from config import path_to_hist_db, apikey_yandex_map_static, colorscheme
import httpx
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

async def flip():
    if random.randint(1, 2) == 2:
        return "Орёл"
    else:
        return "Решка"


async def get_dollar_cost(non: None):
    URL = "https://ru.investing.com/currencies/usd-rub"
    async with httpx.AsyncClient() as client:
        page = await client.get(URL)
        soup = BeautifulSoup(page.text, "lxml")
        cost = soup.find('div', class_="text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]")
        return cost.text


def db_history():
    db = sq.connect(path_to_hist_db)
    return db


def db_hist_init():
    db = db_history()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        AUTHOR TEXT,
        AUTHOR_ID TEXT,
        CONTENT TEXT,
        CHANNEL TEXT,
        CHANNEL_ID TEXT,
        TIME TEXT,
        ACTION TEXT
                )
    """)
    cur.close()
    db.close()


# Проверка на модера по контексту
async def moder(ctx):
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            return True
    if right == 0:
        return False
    
# Проверка на модера по объекту пользователя
async def moder_for_user(user):
    author_roles = user.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            return True
    if right == 0:
        return False
    

# Для асинхронного обращения к API
class API_r():
    async def get_request_json_raw(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                req = await client.get(url)
                req = req.json()
                return req
            except Exception as e:
                return f"Ошибка! Подробнее: {e}"
        
    async def get_request_json(self, atr :str, url: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                req = await client.get(url)
                req = req.json()
                return req[atr]
            except Exception as e:
                return f"Ошибка! Подробнее: {e}"    
        
    
    
    async def get_request(self, url: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                return resp
        except Exception as e:
            return f"Ошибка! Подробнее: {e}"



async def get_iss_loc():
    ap = API_r()
    location = (await ap.get_request_json_raw("http://api.open-notify.org/iss-now.json"))['iss_position']
    return location



async def link_iss_map_form(latitude: str, longitude: str):
    api_url = f"https://static-maps.yandex.ru/v1?apikey={apikey_yandex_map_static}&ll={longitude},{latitude}&z=2&size=450,450&theme=dark&pt={longitude},{latitude},round"
    return api_url  


async def get_count_hist_for_mouth(mounth: int, year: int):
    conn = sq.connect('hist.db')
    cursor = conn.cursor() # Подключение к бд

    cursor.execute("""
    SELECT 
        strftime('%Y-%m-%d', TIME) AS DAY,
        COUNT(*) AS COUNT
    FROM 
        history
    WHERE 
        strftime('%Y-%m', TIME) = ? AND ACTION = 'WRITE'
    GROUP BY 
        strftime('%Y-%m-%d', TIME)
    ORDER BY 
        DAY;
    """, (f'{year}-{mounth:02d}',)) # Запрос к бд

    data = cursor.fetchall()
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
    cursor.close()
    conn.close()
    plt.close()
    return buf



# Круговая диограмма. Распределение сообщений по каналам сервера
async def get_channels_statistic(mounth: int, year: int):
    conn = sq.connect('hist.db')
    cursor = conn.cursor() # Подключение к бд

    cursor.execute("""
    SELECT 
        CHANNEL,
        COUNT(*) AS COUNT
    FROM 
        history
    WHERE 
        strftime('%Y-%m', TIME) = ? AND ACTION = 'WRITE'
    GROUP BY 
        CHANNEL
    ORDER BY 
        COUNT DESC;
    """, (f'{year}-{mounth:02d}',))
    
    
    data = cursor.fetchall()
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
    plt.pie(counts, labels=labels, explode=explodee, colors=colorscheme)
    plt.title(f"Распределение сообщений по каналам сервера за {year}-{mounth}")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


# Круговая диограмма статистики по авторам
async def get_author_stat(mounth: int, year: int):
    conn = sq.connect('hist.db')
    cursor = conn.cursor() # Подключение к бд

    cursor.execute("""
    SELECT 
        AUTHOR,
        COUNT(*) AS COUNT
    FROM 
        history
    WHERE 
        strftime('%Y-%m', TIME) = ? AND ACTION = 'WRITE'
    GROUP BY 
        AUTHOR
    ORDER BY 
        COUNT DESC;
    """, (f'{year}-{mounth:02d}',))
    
    
    data = cursor.fetchall()
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
    cursor.close()
    conn.close()
    return buf


