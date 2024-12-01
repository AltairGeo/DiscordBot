from datetime import datetime
import discord
import discord.ext.commands
import config
import discord.ext
import asyncio
import httpx
import collections
import feedparser
import pytz
from log import logging
from db import db
from cogs import moders, misc, charts

intents = discord.Intents.all()
intents.reactions = True

hist = db()
bot = discord.Bot(intents=intents)

moders.setup(bot=bot)
misc.setup(bot=bot)
charts.setup(bot=bot)


# Действия при запуске бота
@bot.event
async def on_ready():
    print("Bot started!")
    logging.info("Bot started")
    post_q = collections.deque(maxlen=120)
    httpx_client = httpx.AsyncClient()
    num_of_test_char = 70
    # вызов асинхронного парсера rss ленты и выставление параметров
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.custom, name="0_0"))
    await meduza_news(num_of_test_char, post_q, httpx_client)
    logging.info("Meduza parser is started")


# Реакция на удаление участника
@bot.event
async def on_member_remove(member):
    logging.info(f"User {member.name} leave a server")
    channel = member.guild.system_channel
    embed = discord.Embed(title='',
                          description=f"*{member.name}* покинул сервер",
                          color=discord.Color.red())
    await channel.send(embed=embed)


# Реакция на бан участника
@bot.event
async def on_member_ban(guild, user):
    logging.info(f"User {user.name} was banned on server {guild.name}")
    channel = guild.system_channel
    embed = discord.Embed(title='**ЗАБАНЕН**',
                          description=f"*{user.name}* был забанен на сервере",
                          color=discord.Color.red())
    await channel.send(embed=embed)


# Реакция на присоединение участника
@bot.event
async def on_member_join(member: discord.member.Member):
    logging.info("Member joins!")
    embed = discord.Embed(title="**Новый участник!**",
                          description=f"Добро пожаловать на сервер,"
                          f" {member.mention}!",
                          color=discord.Color.green())
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
        except Exception as e:
            logging.warning(f"Falls request. Meduza parser: {e}")
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
            news_text = f'## {title}\n>>> {summary_ready}\n\n'
            f'{date_r}\n[Ссылка на статью.]({link})\n_'
            head = news_text[:num_of_test_char]
            if head in post_query:
                continue
            post_query.appendleft(head)
            # print(news_text)
            if firstly_indicator == 1:
                logging.debug("One of the newsletters has been sent")
                await channel.send(news_text)
        firstly_indicator = 1
        await asyncio.sleep(20)


#########################
#  HISTORY OF MESSAGES  #
#########################


@bot.listen()
async def on_message(message: discord.Message):
    logging.info("Message processing")
    author, author_id, content, chanel, chanel_id = message.author.name, message.author.id, message.content, message.channel, message.channel.id
    if author == "PyBot":
        pass
    else:
        moscow = pytz.timezone('Europe/Moscow')
        loop = asyncio.get_event_loop()
        db = await hist.conn_create(loop=loop)
        cur = await db.cursor()
        await cur.execute("""
        INSERT INTO history (
            AUTHOR, AUTHOR_ID, CONTENT, CHANNEL, CHANNEL_ID, TIME, ACTION
                    ) VALUES (%s, %s, %s, %s, %s, %s, "WRITE")
        """, (str(author),
              str(author_id),
              str(content),
              str(chanel),
              str(chanel_id),
              str(message.created_at.astimezone(moscow))))
        await db.commit()
        await cur.close()
        content = f"```{content[:512]}```"
        logs = await bot.fetch_channel(config.log_channel_id)
        embed = discord.Embed(color=discord.Color.yellow(),
                              title="Отправленно сообщение!",
                              description=f"**Author:** {str(author)}\n"
                              "**Channel:** {str(chanel)}")
        embed.add_field(name="Content", value=str(content))
        await logs.send(embed=embed)


@bot.listen()
async def on_message_delete(message: discord.Message):
    logging.info("Message delete processing")
    author, author_id, content, chanel, chanel_id = message.author.name, message.author.id, message.content, message.channel, message.channel.id
    loop = asyncio.get_event_loop()
    db = await hist.conn_create(loop=loop)
    cur = await db.cursor()
    await cur.execute("""
        INSERT INTO history (
            AUTHOR, AUTHOR_ID, CONTENT, CHANNEL, CHANNEL_ID, TIME, ACTION
                    ) VALUES (%s, %s, %s, %s, %s, %s, "DELETE")
        """, (str(author),
              str(author_id),
              str(content),
              str(chanel),
              str(chanel_id),
              str(datetime.now())))

    await db.commit()
    await cur.close()
    content = f"```{content[:512]}```"
    logs = await bot.fetch_channel(config.log_channel_id)
    embed = discord.Embed(color=discord.Color.red(),
                          title="Удалено сообщение!",
                          description=f"**Author:** {str(author)}\n"
                          "**Channel:** {str(chanel)}")
    embed.add_field(name="Content", value=content)
    await logs.send(embed=embed)

############################################


if __name__ == "__main__":
    logging.info("bot starting...")
    bot.run(config.TOKEN)
