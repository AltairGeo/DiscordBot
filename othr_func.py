import requests
from bs4 import BeautifulSoup
from config import model
from openai import OpenAI
import sqlite3 as sq
from config import path_to_hist_db




def get_dollar_cost(non: None):
    URL = "https://ru.investing.com/currencies/usd-rub"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "lxml")
    cost = soup.find('div', class_="text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]")
    return cost.text


def ai_forget():
    try:
        client = OpenAI(
        base_url = 'http://localhost:11434/v1',
        api_key='ollama',
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return "Контекст забыт!"
    except Exception as e:
        return f"Ошибка: {e}"

def ai_resp(prompt: str):
    try:
        client = OpenAI(
        base_url = 'http://localhost:11434/v1',
        api_key='ollama',
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {e}"



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