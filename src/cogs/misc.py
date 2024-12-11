from discord.ext import commands
import discord
from log import logging
import othr_func as func
from translate import Translator
from io import BytesIO
import config
import discord_ui as uui
import WikiLib as wl


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Орёл или решка?")
    async def flip(self, ctx):
        logging.info("the /flip was used")
        await ctx.respond(await func.flip())

    @discord.slash_command(description="Количество участников на сервере.")
    async def members_count(self, ctx):
        logging.info("the /membrers_count was used")
        await ctx.respond(f"На сервере {ctx.guild.member_count} человек.")

    @discord.slash_command(description="Зачем это тут?")
    async def fox(self, ctx):
        logging.info("the /fox was used")
        ap = func.API_r()
        resp = await ap.get_request_json(atr="image", url="https://randomfox.ca/floof/")
        await ctx.respond(resp)

    @discord.slash_command(description="Да.")
    async def yes_gif(self, ctx):
        logging.info("the /yes_gif was used")
        ap = func.API_r()
        resp = await ap.get_request_json(atr="image", url="https://yesno.wtf/api?force=yes")
        await ctx.respond(resp)

    @discord.slash_command(description="Нет.")
    async def no_gif(self, ctx):
        logging.info("the /no_gif was used")
        ap = func.API_r()
        resp = await ap.get_request_json(atr="image", url="https://yesno.wtf/api?force=no")
        await ctx.respond(resp)

    @discord.slash_command(description="В окно посмотреть, никак?")
    # wttr.in
    async def weather(self, ctx, city: str):
        logging.info("the /weather was used")
        ct = city
        city = city.replace(" ", "+")
        url = f"https://wttr.in/{city}?Q0n&lang=ru"
        logging.debug("Weather: url formed")
        api = func.API_r()
        try:
            await ctx.respond("Обработка...")
            logging.debug("Weather: send request for wttr.in")
            resp = await api.get_request(url)
            embed = discord.Embed(title=f'Погода в {ct}', description=f"```ansi\n{resp.text}```", color=discord.Color.green())
            logging.debug("Weather: embed formed")
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Weather error: {e}")
            await ctx.send(f"Ошибка: {e}")

    @discord.slash_command(description="Фаза луны.")
    # wttr.in/moon
    async def moon(self, ctx):
        logging.info("the /moon was used")
        url = "https://wttr.in/moon?T0&lang=ru"
        api = func.API_r()
        try:
            await ctx.respond("Обработка...")
            logging.debug("moon: Send request to wttr.in")
            resp = await api.get_request(url)
            await ctx.send(f"```ansi\n{resp.text}```")
        except Exception as e:
            logging.error(f"moon error: {e}")
            await ctx.send(f"Ошибка: {e}")

    @discord.slash_command(description="Случайный факт о числе.")
    # http://numbersapi.com/
    async def fact_about_number(self, ctx, num: int):
        logging.info("the /fact_about_number was used")
        url = f"http://numbersapi.com/{str(num)}"
        try:
            api = func.API_r()
            logging.debug("Send request to numbersapi.com")
            resp = await api.get_request(url)
            translatorr = Translator(from_lang='en', to_lang='ru')
            respond = f"EN: {resp.text}\nRU: {translatorr.translate(resp.text)}"
            await ctx.respond(respond)
        except Exception as e:
            logging.error(f"fact_about_number error: {e}")
            await ctx.send(f"Ошибка! {e}")

    @discord.slash_command(description="Котики!")
    # https://catfact.ninja/fact
    async def cat_fact(self, ctx: discord.ApplicationContext):
        await ctx.respond("Обработка...")
        logging.info("the /cat_fact was used")
        api = func.API_r()
        logging.debug("cat_fact: send request to catfact.ninja/fact")
        resp = await api.get_request_json(atr="fact", url="https://catfact.ninja/fact")
        translatorr = Translator(from_lang='en', to_lang='ru')
        embed = discord.Embed(title="Интересный факт", color=discord.Color.green())
        embed.add_field(name="EN", value=f"{resp}\n")
        embed.add_field(name="RU", value=translatorr.translate(resp))
        await ctx.send(embed=embed)

    async def fetch_image(self, url):
        api = func.API_r()
        response = await api.get_request(url)
        return response.content

    @discord.slash_command(description="Местоположение МКС.")
    # ISS location
    async def iss_location(self, ctx):
        logging.info("the /iss_location was used")
        await ctx.respond("Обработка...")
        try:
            logging.debug("iss_location: try to request iss location")
            iss = await func.get_iss_loc()   # Получение координат мкс
            logging.debug("iss_location: try to request url for map image")
            api_url = await func.link_iss_map_form(iss['latitude'], iss['longitude'])  # формирование запроса к api yandex map static
            logging.debug("iss_location: try to fetcg map image")
            image_data = await self.fetch_image(api_url)  # получение изображения карты
            file = discord.File(BytesIO(image_data), filename='image.png')
            await ctx.send("# Текущее расположение МКС.", file=file)
        except Exception as e:
            await ctx.send(f"Ошибка! Подробнее: {e}")

    @discord.slash_command(description="Список людей в космосе.")
    # Количество людей в космосе
    async def people_in_space(self, ctx):
        logging.info("the /people_in_space was used")
        await ctx.respond("Обработка...")
        url = "http://api.open-notify.org/astros.json"
        try:
            empty = " "
            api = func.API_r()
            logging.debug("people_in_space: try to get people list")
            resp = await api.get_request_json_raw(url)
            people = "```\n+---------------------------+---------------------------------------+\n|           Имя             |               Станция                 |\n+---------------------------+---------------------------------------+\n"
            for i in resp['people']:
                people += f"|{empty * 3}{i['name']}{empty * (24 - len(i['name']))}|{empty * 3}{i['craft']}{empty * (36 - len(i['craft']))}|\n"
            final = f"# На данный момент в космосе {str(resp['number'])} человек вот их список:satellite_orbital::\n{people}+---------------------------+---------------------------------------+```"
            logging.debug("people_in_space: complete list forming")
            await ctx.send(final)
        except Exception as e:
            logging.error(f"people_in_space: ERROR! {e}")
            await ctx.send(f"Ошибка! Подробнее: {e}")

    @discord.slash_command(description="Кто я?")
    async def i_moder(self, ctx):
        logging.info("the /i_moder was used")
        resp = await func.moder(ctx)
        await ctx.respond(str(resp))

    @discord.slash_command(description="Нет слов.")
    async def get_my_avatar(self, ctx):
        logging.info("the /get_my_avatar was used")
        embed = discord.Embed(title=f'Аватар пользователя {ctx.author.name}',
                              color=discord.Color.green())
        embed.set_image(url=ctx.author.avatar)
        await ctx.respond(embed=embed)

    @discord.slash_command(description="Божье творенье.")
    async def get_server_avatar(self, ctx):
        logging.info("the /get_server_avatar was used")
        embed = discord.Embed(title=f'Аватар сервера {ctx.guild.name}',
                              color=discord.Color.green())
        if ctx.guild.icon is None:
            await ctx.respond("У сервера нет иконки.")
            return None
        embed.set_image(url=ctx.guild.icon)
        await ctx.respond(embed=embed)

    @discord.slash_command(description="QR")
    async def qr(self, ctx: discord.ApplicationContext, data: str):
        logging.info("the /qr was used")
        image = await self.fetch_image(f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}&color=000000&margin=20")
        file = discord.File(BytesIO(image), filename='qr.png')
        await ctx.respond(file=file)

    @discord.slash_command(description="QR наоборот")
    async def qr_invert(self, ctx: discord.ApplicationContext, data: str):
        logging.info("the /qr was used")
        image = await self.fetch_image(f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}&color=ffffff&bgcolor=000000&margin=20")
        file = discord.File(BytesIO(image), filename='qr.png')
        await ctx.respond(file=file)

    @discord.slash_command(description="Вы видели курс?!")
    # Цена доллара
    async def dollarcost(self, ctx):
        cost = await func.get_dollar_cost()
        stor = f"1$ = {cost}₽"
        logging.info("The /dollarcost was used")
        await ctx.respond(stor)

    @discord.slash_command(description="Случайная статья из википедии.")
    # Модуль рандомной статьи из вики
    async def grws(self, ctx):
        logging.info("the /grws was used")
        if config.ENABLE_WIKI_MODULE == 1:
            wiki_engine = wl.WikiLib(config.WIKI_URL)
            name = wiki_engine.get_name()
            text = wiki_engine.get_text()
            link = wiki_engine.get_self_link(1)
            res = f"{name} \n{text}"
            result = ""
            count = 0
            for i in res:
                count += 1
                if count >= 700:
                    result += "..."
                    break
                result += i
            result += f"\n {link}"
            logging.debug("grws engine complete parsing")
            embed = discord.Embed(title='Случайная статья из википедии',
                                  color=discord.Color.green())
            embed.add_field(name='Содержимое', value=result, inline=False)
            try:
                embed.set_image(url=wiki_engine.get_picture())
            except Exception as e:
                print(e)
            logging.debug("grws created a embed")
            await ctx.respond(embed=embed)
        else:
            logging.warning("ENABLE_WIKI_MODULE = 0")
            await ctx.respond("Вики-Модуль выключен!")

    @discord.slash_command(description="Переводчик")
    async def translate(self, ctx, message: str):
        logging.info("the /translate was used")
        await ctx.respond(view=uui.TranslatorView(messages=message))


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
