from datetime import timedelta, datetime
import discord
from discord.ext import tasks
import discord.ext.commands
import config
import discord.ext
import dswarn
import WikiLib as wl
import othr_func as func
from translate import Translator
import asyncio
import httpx
import collections
import feedparser
import pytz
from io import BytesIO
from typing import Optional
from log import logging
import discord_ui as uui


intents = discord.Intents.all()

#Класс выбора для переводчика
class TranslatorView(discord.ui.View):
    def __init__(self, messages):
        super().__init__()
        self.messagee = messages
        #print(self.message)
    
    @discord.ui.select(
        placeholder = "Выбери язык:",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(label="Ru to En"),
            discord.SelectOption(label="En to Ru")
        ]
    )
    async def select_callback(self, select, interaction):
        message_trans = str(self.messagee)
        result = select.values[0]
        if result == "Ru to En":
            translatorr = Translator(from_lang='ru', to_lang='en')
            transs = translatorr.translate(message_trans)
            await interaction.response.send_message(f"Перевод: {transs}")       
        elif result == "En to Ru":
            translator = Translator(from_lang='en', to_lang='ru')
            trans = translator.translate(message_trans)
            await interaction.response.send_message(f"Перевод: {trans}")

               
bot = discord.Bot(intents=intents)





#Действия при запуске бота
@bot.event
async def on_ready():
    print("Bot started!")
    logging.info("Bot started")
    post_q = collections.deque(maxlen=120)
    httpx_client = httpx.AsyncClient()
    num_of_test_char = 70
    # вызов асинхронного парсера rss ленты и выставление параметров
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="0_0"))    
    await meduza_news(num_of_test_char, post_q, httpx_client)
    logging.info("Meduza parser is started")

@bot.event
async def on_member_remove(member):
    logging.info(f"User {member.name} leave a server")
    channel = member.guild.system_channel
    embed = discord.Embed(title='', description=f"*{member.name}* покинул сервер", color=discord.Color.red())
    await channel.send(embed=embed)


@bot.event
async def on_member_ban(guild, user):
    logging.info(f"User {user.name} was banned on server {guild.name}")
    channel = guild.system_channel
    embed = discord.Embed(title='**ЗАБАНЕН**', description=f"*{user.name}* был забанен на сервере", color=discord.Color.red())
    await channel.send(embed=embed)


@bot.event
async def on_member_join(member: discord.member.Member):
    logging.info("Member joins!")
    embed = discord.Embed(title="**Новый участник!**", description=f"Добро пожаловать на сервер, {member.mention}!", color=discord.Color.green())
    await member.guild.system_channel.send(embed=embed)



# Парсинг rss ленты meduza.io
async def meduza_news(num_of_test_char, post_query, httpx_client):
    guild = bot.get_guild(int(config.SERVER_ID))
    channel = guild.get_channel(int(config.news_id))
    rss_link = 'https://meduza.io/rss2/all'
    firstly_indicator = 0
    while True:
        try:
            resurs = await httpx_client.get(rss_link)
            logging.debug("Meduza parser, request fulfilled ")
        except:
            logging.warning("Falls request. Meduza parser")
            await asyncio.sleep(10)
            continue

        feed = feedparser.parse(resurs.text)

        for i in feed['entries']:
            title = i['title']
            summary = i['summary']
            summary_ready = summary.replace("<p>", "")
            date = i['published']
            date_r = date.replace("+0300", "")
            link = i['link']
            news_text = f'## {title}\n>>> {summary_ready}\n\n{date_r}\n[Ссылка на статью.]({link})\n_'
            head = news_text[:num_of_test_char]
            if head in post_query:
                continue
            post_query.appendleft(head)
            #print(news_text)
            if firstly_indicator == 1:
                logging.debug("One of the newsletters has been sent")
                await channel.send(news_text)
        firstly_indicator = 1
        await asyncio.sleep(20)


@bot.command()
async def gtn(ctx):
    """A Slash Command to play a Guess-the-Number game."""

    await ctx.respond('Guess a number between 1 and 10.')
    guess = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    if int(guess.content) == 5:
        await ctx.send('You guessed it!')
    else:
        await ctx.send('Nope, try again.')


# Цена доллара
@bot.slash_command()
async def dollarcost(ctx):
    cost = await func.get_dollar_cost(None)
    stor = f"1$ = {cost}₽"
    logging.info("The /dollarcost was used")
    await ctx.respond(stor)


@bot.slash_command(description="Дать предупреждение пользователю.")
async def addwarn(ctx: discord.ApplicationContext):
    if await func.moder(ctx=ctx):
        await ctx.respond("Выбор пользователя:", view=uui.TargetSelectView())
    else:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


# Дать предупреждение
@bot.slash_command(description="Дать предупреждение пользователю.")
async def addwarn_legacy(ctx: discord.ApplicationContext, name: discord.Member, reason: str):
    logging.info("the /addwarn was used")
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            user_id = name.id
            user_name = name.name 
            await ctx.respond(dswarn.add_warn(user_id, user_name, reason))
            logging.debug(f"Add warn to {user_name} for reason: {reason}")
            result = await dswarn.warn_system(user_id)
            if result == 100:
                await name.timeout_for(timedelta(minutes=20))
            elif result == 105:
                await name.timeout_for(timedelta(hours=6))
            elif result == 200:
                await name.timeout_for(reason="16 предупреждений")
            right = 1
    if right == 0:
        await ctx.respond("У вас нет прав на выполнение данной команды!")

    


@bot.slash_command(description="Удалить предупреждение у пользователя по id.")
async def delwarn_legacy(ctx, id_warn: int):
    logging.info("the /delwarn was used")
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            await ctx.respond(dswarn.delete_warn(id_warn))
            logging.debug(f"Deleted warning with id = {id_warn}")
            right = 1
    if right == 0:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


# Все предупреждения пользователя
@bot.slash_command(description="Показать все предупреждения пользователя")
async def alluserwarn(ctx: discord.ApplicationContext, name: discord.Member):
    logging.info("the /alluserwarn was used")
    if await func.moder(ctx):
        await ctx.respond("Обработка!")
        for i in dswarn.all_user_warn(name.id):
            embed = discord.Embed(title=f"{i[2]}", description=f"Причина: {i[3]}", color=discord.Color.dark_green())
            embed.set_footer(text=f"warn_id: {i[0]}")
            await ctx.send(embed=embed, view=uui.AllUserWarns(i[0]))
    else:
        await ctx.send("У вас нет прав на выполнение данной команды!")


# мут
@bot.slash_command(description="Дать мут на определённое кол-во часов.")
async def mute(ctx: discord.ApplicationContext, name: discord.Member, hours: int):
    logging.info("the /mute was used")
    delta = timedelta(hours=hours)
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            await ctx.respond("Обработка...")
            await name.timeout_for(delta)
            logging.debug(f"{name.name} is get mute for {hours} hours.")
            embed = discord.Embed(title=f"{name.name}", description=f"Выдан мут на {hours} часов.", color=discord.Color.red())
            await ctx.send(embed=embed)
            right = 1
    if right == 0:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


#Модуль рандомной статьи из вики 
@bot.slash_command(description="Рандомная статья из википедии")
async def grws(ctx):
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
        embed = discord.Embed(title='Случайная статья из википедии', color=discord.Color.green())
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


@bot.slash_command(description="Переводчик")
async def translate(ctx, message: str):
    logging.info("the /translate was used")
    await ctx.respond(view=TranslatorView(messages=message))

##########
# Разное #
##########


@bot.slash_command()
async def flip(ctx):
    logging.info("the /flip was used")
    await ctx.respond(await func.flip())


@bot.slash_command(description="Количество участников на сервере.")
async def members_count(ctx):
    logging.info("the /membrers_count was used")
    await ctx.respond(f"На сервере {ctx.guild.member_count} человек.")


@bot.slash_command()
async def fox(ctx):
    logging.info("the /fox was used")
    ap = func.API_r()
    resp = await ap.get_request_json(atr="image", url="https://randomfox.ca/floof/")
    await ctx.respond(resp)


@bot.slash_command()
async def yes_gif(ctx):
    logging.info("the /yes_gif was used")
    ap = func.API_r()
    resp = await ap.get_request_json(atr="image", url="https://yesno.wtf/api?force=yes")
    await ctx.respond(resp)


@bot.slash_command()
async def no_gif(ctx):
    logging.info("the /no_gif was used")
    ap = func.API_r()
    resp = await ap.get_request_json(atr="image", url="https://yesno.wtf/api?force=no")
    await ctx.respond(resp)


@bot.slash_command()
async def weather(ctx, city: str):
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


@bot.slash_command()
async def moon(ctx):
    logging.info("the /moon was used")
    url = "https://wttr.in/moon?T0&lang=ru"
    api = func.API_r()
    try:
        await ctx.respond("Обработка...")
        logging.debug("moon: Send request to wttr.in")
        resp = await api.get_request(url)
        print(resp.text)
        #embed = discord.Embed(title=f'Фаза луны', description=f"```ansi\n{resp.text}```", color=discord.Color.green())
        #await ctx.send(embed=embed)
        await ctx.send(f"```ansi\n{resp.text}```")
    except Exception as e:
        logging.error(f"moon error: {e}")
        await ctx.send(f"Ошибка: {e}")


#http://numbersapi.com/
@bot.slash_command()
async def fact_about_number(ctx, num: int):
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


#https://catfact.ninja/fact
@bot.slash_command()
async def cat_fact(ctx: discord.ApplicationContext):
    await ctx.respond("Обработка...")
    logging.info("the /cat_fact was used")
    api = func.API_r()
    logging.debug("cat_fact: send request to catfact.ninja/fact")
    resp = await api.get_request_json(atr="fact", url="https://catfact.ninja/fact")
    translatorr = Translator(from_lang='en', to_lang='ru')
    await ctx.send(f"EN: {resp}\n-------------------------------------------------------------------\nRU: {translatorr.translate(resp)}")


async def fetch_image(url):
    api = func.API_r()
    response = await api.get_request(url)
    return response.content


# ISS location
@bot.slash_command()
async def iss_location(ctx):
    logging.info("the /iss_location was used")
    await ctx.respond("Обработка...")
    try:
        logging.debug("iss_location: try to request iss location")
        iss = await func.get_iss_loc() # Получение координат мкс
        logging.debug("iss_location: try to request url for map image")
        api_url = await func.link_iss_map_form(iss['latitude'], iss['longitude']) # формирование запроса к api yandex map static
        logging.debug("iss_location: try to fetcg map image")
        image_data = await fetch_image(api_url) # получение изображения карты
        file = discord.File(BytesIO(image_data), filename='image.png')
        await ctx.send("# Текущее расположение МКС.", file=file)
    except Exception as e:
        await ctx.send(f"Ошибка! Подробнее: {e}")


# Количество людей в космосе
@bot.slash_command()
async def people_in_space(ctx):
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


@bot.slash_command()
async def i_moder(ctx):
    logging.info("the /i_moder was used")
    resp = await func.moder(ctx)
    await ctx.respond(str(resp))


@bot.slash_command()
async def top7_author_stat(ctx, year: int, month: int):
    logging.info("the /author_stat was used")
    moder = await func.moder(ctx)
    
    if moder == True:
        await ctx.respond("Обработка...")
        logging.debug("top7_author_stat: get hist for author")
        resp = await func.get_author_stat(year=year, mounth=month)
        if resp == None:
            await ctx.send("Ничего не найдено.")
        else:
            await ctx.send(file=discord.File(resp, filename='author_stat.png'))
    else:
        await ctx.respond("У вас нет прав на выполнение данной команды!")



# Статистика сообщений за месяц
@bot.slash_command()
async def month_statistic(ctx, year: int, month: int):
    logging.info("the /month_statistic was used")
    moder = await func.moder(ctx)
    if moder == True:
        await ctx.respond("Обработка...")
        logging.debug("month_statistic: get hist for month")
        resp = await func.get_count_hist_for_mouth(month, year)
        if resp == None:
            await ctx.send("Ничего не найдено.")
        else:
            await ctx.send(file=discord.File(resp, filename='hist_for_mouth.png'))
    else:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


@bot.slash_command()
async def channel_statistics(ctx, year: int, month: int):
    logging.info("the /channel_statistics was used")
    moder = await func.moder(ctx)
    if moder == True:
        await ctx.respond("Обработка...")
        logging.debug("channel_statistic: get channel statistic")
        resp = await func.get_channels_statistic(month, year)
        if resp == None:
            await ctx.respond("Ничего не найдено.")
        else:
            await ctx.send(file=discord.File(resp, filename='hist_for_mouth.png'))
    else:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


##############################################
###   Получение всех сообщений за день     ###
##############################################


@bot.slash_command()
async def get_day_hist(ctx, day: int, mounth: int, year: int):
    logging.info("the /get_day_hist was used")
    await ctx.respond("Обработка...")
    moder = await func.moder(ctx)
    if moder == True:
        logging.debug("get_day_hist: get all history for day")
        ls = await func.get_hist_for_day(day, mounth, year)
        if ls == []:
            await ctx.send("Ничего не найдено.")
        for i in ls:
            await ctx.send(f"**Author:** {i['author']}\n**Content:** ```{i['message']}```\n**Channel:** {i['channel']}\n**Time:**{i['time']}")
    else:
        ctx.respond("У вас нет прав на выполнение данной команды!")


#############################
###  HISTORY OF MESSAGES  ###
#############################


@bot.listen()
async def on_message(message: discord.Message):
    logging.info("Message processing")
    author, author_id, content, chanel, chanel_id = message.author.name, message.author.id, message.content, message.channel, message.channel.id
    if author == "PyBot":
        pass
    else:
        moscow = pytz.timezone('Europe/Moscow')
        db = func.db_history()
        cur = db.cursor()
        cur.execute("""
        INSERT INTO history (
            AUTHOR, AUTHOR_ID, CONTENT, CHANNEL, CHANNEL_ID, TIME, ACTION
                    ) VALUES (?, ?, ?, ?, ?, ?, "WRITE")
        """, (str(author), str(author_id), str(content), str(chanel), str(chanel_id), str(message.created_at.astimezone(moscow))))
        #print(str(author), str(author_id), str(content), str(chanel), str(chanel_id), str(message.created_at.astimezone(moscow)))
        db.commit()
        db.close()
    

@bot.listen()
async def on_message_delete(message: discord.Message):
    logging.info("Message delete processing")
    author, author_id, content, chanel, chanel_id = message.author.name, message.author.id, message.content, message.channel, message.channel.id
    db = func.db_history()
    cur = db.cursor()
    cur.execute("""
    INSERT INTO history (
        AUTHOR, AUTHOR_ID, CONTENT, CHANNEL, CHANNEL_ID, TIME, ACTION
                ) VALUES (?, ?, ?, ?, ?, ?, "DELETE")
    """, (str(author), str(author_id), str(content), str(chanel), str(chanel_id), str(datetime.now())))
    #print(str(author), str(author_id), str(content), str(chanel), str(chanel_id), str(datetime.now()))
    db.commit()
    db.close()


# Как делать Embed

#@bot.slash_command()
#async def send_embed(ctx):
#    ap = func.API_r()
#    # Создание embed
#    embed = discord.Embed(title='Пример Embed', description='Это пример embed-сообщения.', color=discord.Color.blue())
#    # Добавление поля
#    embed.add_field(name='Поле 1', value='Значение поля 1', inline=False)
#    
#    # Добавление изображения
#    embed.set_image(url=await ap.get_request_json(atr="image", url="https://randomfox.ca/floof/"))
#    
#    # Добавление футера
#    embed.set_footer(text='Это футер embed-сообщения.')
#    
#    # Отправка embed
#   
#  await ctx.respond(embed=embed)


@bot.slash_command()
async def get_my_avatar(ctx):
    logging.info("the /get_my_avatar was used")
    embed = discord.Embed(title=f'Аватар пользователя {ctx.author.name}',color=discord.Color.green())
    embed.set_image(url=ctx.author.avatar)
    await ctx.respond(embed=embed)


@bot.slash_command()
async def get_server_avatar(ctx):
    logging.info("the /get_server_avatar was used")
    embed = discord.Embed(title=f'Аватар сервера {ctx.guild.name}',color=discord.Color.green())
    if ctx.guild.icon == None:
        await ctx.respond("У сервера нет иконки.")
        return None
    embed.set_image(url=ctx.guild.icon)
    await ctx.respond(embed=embed)



############
# Опросы   #
############


@bot.slash_command(name='poll')
async def create_poll(ctx, question: str,option1: str, option2:str, option3: Optional[str] = None, option4: Optional[str] = None, option5: Optional[str] = None, option6: Optional[str] = None, option7: Optional[str] = None, option8: Optional[str] = None, option9: Optional[str] = None, option10: Optional[str] = None):
    logging.info("the /create_poll was used")
    if await func.moder(ctx) == True:
        await ctx.respond("Обработка...")
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '10️⃣']
        options = []
        reacts = []
        options.append(option1)
        options.append(option2)
        reacts.append(reactions[0])
        reacts.append(reactions[1])

        if option3 is not None:
            options.append(option3)
            reacts.append(reactions[2])
        if option4 is not None:
            options.append(option4)
            reacts.append(reactions[3])
        if option5 is not None:
            options.append(option5)
            reacts.append(reactions[4])
        if option6 is not None:
            options.append(option6)
            reacts.append(reactions[5])
        if option7 is not None:
            options.append(option7)
            reacts.append(reactions[6])
        if option8 is not None:
            options.append(option8)
            reacts.append(reactions[7])
        if option9 is not None:
            options.append(option9)
            reacts.append(reactions[8])
        if option10 is not None:
            options.append(option10)
            reacts.append(reactions[9])

        desc = ""
        counter = 0
        for i in options:
            desc += f"{reacts[counter]} {options[counter]}\n"
            counter += 1
        
        embed = discord.Embed(title=question, description=desc, color=discord.Color.green())
        message = await ctx.send(embed=embed)
        for reaction in reacts:
            await message.add_reaction(reaction)
    else:
        ctx.respond("У вас нет прав на выполнение данной команды!")


@bot.slash_command()
async def show_poll(ctx, message_id: str):
    logging.info("the /show_poll was used")
    if await func.moder(ctx) == True:
        try:
            message = await ctx.channel.fetch_message(message_id)
        except discord.HTTPException:
            await ctx.respond('Сообщение не найдено.')
            return None

        reactions = message.reactions
        results = {}

        for reaction in reactions:
            results[reaction.emoji] = reaction.count - 1  # Вычитаем 1, чтобы не учитывать реакцию бота

        x = []
        y = []
        co = 0
        react = ["Кандидат 1", "Кандидат 2", "Кандидат 3", "Кандидат 4", "Кандидат 5", "Кандидат 6", "Кандидат 7", "Кандидат 8", "Кандидат 9", "Кандидат 10"]
        for reaction, count in results.items():
            x.append(react[co])
            y.append(count)
            co += 1

        await ctx.respond("Обработка...")
        resp = await func.stolb(x, y)
        if resp == None:
            await ctx.send("Ничего не найдено.")
        else:
            await ctx.send(file=discord.File(resp, filename='poll.png'))
    else:
        await ctx.respond("У вас нет прав на использование данной команды.")
    


##########################################################################


if __name__ == "__main__":
    logging.info("hist_db init...")
    func.db_hist_init()
    logging.info("bot starting...")
    bot.run(config.TOKEN)

