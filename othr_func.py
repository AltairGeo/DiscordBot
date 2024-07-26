import requests
import discord
from bs4 import BeautifulSoup

def get_dollar_cost():
    URL = "https://ru.investing.com/currencies/usd-rub"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "lxml")
    cost = soup.find('div', class_="text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]")
    return cost.text



