from bs4 import BeautifulSoup
import config, random
from openai import OpenAI
import sqlite3 as sq
from config import path_to_hist_db, apikey_yandex_map_static
import httpx
import datetime
import matplotlib.pyplot as plt
from io import BytesIO




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



async def get_hist_for_day(day: int, mounth: int, year: int):
    conn = sq.connect('hist.db')
    cursor = conn.cursor() # Подключение к бд

    cursor.execute("SELECT * FROM history WHERE ACTION = 'WRITE'") # Запрос к бд
    columns = [desc[0] for desc in cursor.description] # Получение всех колонок бд
    results = cursor.fetchall() 
    filtered_results = []


    for row in results:
        time_str = row[columns.index('TIME')]
        if '+' in time_str: # убираем часовой пояс
            time_str = time_str[0: -6]
        if '.' in time_str:  # Если в строке времени есть микросекунды
            dt = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
        else:  # Если в строке времени нет микросекунд
            dt = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        if dt.month == mounth and dt.year == year and dt.day == day:
            message = row[columns.index('CONTENT')]
            sender = row[columns.index('AUTHOR')]
            channel = row[columns.index('CHANNEL')]
            bubl = {'author': sender,
                    'message': message,
                    'time': str(dt.time()),
                    'channel': channel
                    }
            filtered_results.append(bubl)
    cursor.close()
    conn.close()
    return filtered_results    


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
        datas.append(i[0][-2: ])
        counts.append(i[1])
    buf = BytesIO()
    plt.plot(datas, counts, color='green', marker='.', markersize=7)
    plt.xlabel('Месяц-День')
    plt.ylabel('Количество сообщений') #Подпись для оси y
    plt.title('Кол-во сообщений за месяц по дням')
    #plt.savefig('hist_for_mouth.png')
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
    plt.pie(counts, labels=labels)
    plt.title(f"Распределение сообщений по каналам сервера за {year}-{mounth}")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf



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

    plt.figure(figsize=(10, 6)) 
    plt.pie(counts, labels=labels, autopct='%1.1f%%')
    plt.legend(labels, loc='upper right', bbox_to_anchor=(1.3, 1))
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    cursor.close()
    conn.close()
    return buf


async def flip():
    if random.randint(1, 2) == 2:
        return "Орёл"
    else:
        return "Решка"


async def stolb(x, y):
    plt.bar(x, y, label='Количество голосов', color='#2f6422') #Параметр label позволяет задать название величины для легенды
    plt.xlabel('Варианты')
    plt.ylabel('Кол-во голосов')
    plt.title('Итоги')
    plt.legend()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf