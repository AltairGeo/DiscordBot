from datetime import timedelta
import discord
import config
import warn
import WikiLib as wl
import othr_func as func
from translate import Translator
import asyncio
import httpx
import collections
import feedparser


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

               
bot = discord.Bot()


#Действия при запуске бота
@bot.event
async def on_ready():
    print("Bot started!")
    post_q = collections.deque(maxlen=120)
    httpx_client = httpx.AsyncClient()
    num_of_test_char = 70
    # вызов асинхронного парсера rss ленты и выставление параметров
    await meduza_news(num_of_test_char, post_q, httpx_client)


# Парсинг rss ленты meduza.io
async def meduza_news(num_of_test_char, post_query, httpx_client):
    guild = bot.get_guild(int(config.SERVER_ID))
    channel = guild.get_channel(int(config.news_id))
    rss_link = 'https://meduza.io/rss2/all'
    firstly_indicator = 0
    while True:
        try:
            resurs = await httpx_client.get(rss_link)
        except:
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
            news_text = f'{title}\n{summary_ready}\n\n{date_r}\n{link}\n\n_'
            head = news_text[:num_of_test_char]
            if head in post_query:
                continue
            post_query.appendleft(head)
            print(news_text)
            if firstly_indicator == 1:
                await channel.send(news_text)
        firstly_indicator = 1
        await asyncio.sleep(20)



@bot.slash_command()
async def ping(ctx):
    await ctx.respond("pong")


@bot.slash_command()
async def dollarcost(ctx):
    cost = func.get_dollar_cost(None)
    stor = f"1$ = {cost}₽"
    await ctx.respond(stor)


@bot.slash_command(description="Дать предупреждение пользователю.")
async def addwarn(ctx, name: discord.Member, reason: str):
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            user_id = name.id
            user_name = name.name
            await ctx.respond(warn.add_warn(user_id, user_name, reason))
            right = 1
    if right == 0:
        await ctx.respond("У вас нет прав на выполнение данной команды!")

    list_of_warns = warn.get_count_warn()
    for i in list_of_warns:
        if i[0] == name.id:
            result = warn.counter(i[1])
            if result == 100:
                await name.timeout_for(timedelta(minutes=20))
            elif result == 105:
                await name.timeout_for(timedelta(hours=6))
            elif result == 200:
                await name.ban(reason="16 предупреждений")


@bot.slash_command(description="Удалить предупреждение у пользователя по id.")
async def delwarn(ctx, id_warn: int):
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            await ctx.respond(warn.delete_warn(id_warn))
            right = 1
    if right == 0:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


@bot.slash_command()
async def alluserwarn(ctx, name: discord.Member):
    await ctx.respond(warn.all_user_warn(name.id))


@bot.slash_command(description="Дать мут на определённое кол-во часов.")
async def mute(ctx, name: discord.Member, hours: int):
    delta = timedelta(hours=hours)
    author_roles = ctx.author.roles
    mod = config.MOD_ID
    right = 0
    for i in author_roles:
        i = i.id
        if str(i) == mod:
            await name.timeout_for(delta)
            await ctx.respond(f"Дан мут пользователю {name.name}!")
            right = 1
    if right == 0:
        await ctx.respond("У вас нет прав на выполнение данной команды!")


#Модуль рандомной статьи из вики 
@bot.slash_command()
async def grws(ctx):
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
            if count >= 1500:
                result += "..."
                break
            result += i
        result += f"\n {link}"
        await ctx.respond(result)
            
    else:
        await ctx.respond("Вики-Модуль выключен!")



@bot.slash_command()
async def translate(ctx, message: str):
    #print(message)
    await ctx.respond(view=TranslatorView(messages=message))


@bot.slash_command()
async def ai(ctx, prompt: str):
    ctx.respond(func.ai_resp(prompt))

@bot.slash_command()
async def ai_forget_context():
    ctx.respond(func.ai_forget())


bot.run(config.TOKEN)

