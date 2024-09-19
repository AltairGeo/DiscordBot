import requests, json
from bs4 import BeautifulSoup
from config import  ai_url, model


headers = {
    "Content-Type": "application/json"
}



def get_dollar_cost(non: None):
    URL = "https://ru.investing.com/currencies/usd-rub"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "lxml")
    cost = soup.find('div', class_="text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]")
    return cost.text


def ai_forget():
    data = {
    'model': model,
    'messages': [
        {'role': 'user', 'content': "Forget the context."}
    ]
    }
    response = requests.post(ai_url, json=data)
    if response.status_code == 200:
        return "Контекст очищен!"
    else:
        return "Error!"

def ai_resp(prompt: str):
    data = {
    'model': model,
    'messages': [
        {'role': 'user', 'content': prompt}
    ]
    }
    response = requests.post(ai_url, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Ошибка!", response.status_code, response.text


