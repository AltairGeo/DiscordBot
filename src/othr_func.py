from bs4 import BeautifulSoup
import config
import random
from config import apikey_yandex_map_static
import httpx


async def flip():
    if random.randint(1, 2) == 2:
        return "Орёл"
    else:
        return "Решка"


async def get_dollar_cost() -> str:
    URL = "https://ru.investing.com/currencies/usd-rub"
    async with httpx.AsyncClient() as client:
        page = await client.get(URL)
        soup = BeautifulSoup(page.text, "lxml")
        cost = soup.find('div', class_="text-5xl/9 font-bold text-#232526] md:text-[42px] md:leading-[60px]")
        if cost is None:
            return "Error!"
        return cost.text


# Проверка на модера по контексту
async def moder(ctx) -> bool:
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
async def moder_for_user(user) -> bool:
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

    async def get_request_json(self, atr: str, url: str) -> str:
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
    location = (
        await ap.get_request_json_raw(
            "http://api.open-notify.org/iss-now.json"))['iss_position']
    return location


async def link_iss_map_form(latitude: str, longitude: str):
    api_url = f"https://static-maps.yandex.ru/v1?apikey={apikey_yandex_map_static}&ll={longitude},{latitude}&z=2&size=450,450&theme=dark&pt={longitude},{latitude},round"
    return api_url
