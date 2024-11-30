import discord
from discord.ext import commands
import othr_func as func
from log import logging
import asyncio
from stats import stats


class Charts(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @discord.slash_command(description="Статистика распределения сообщений за месяц по участникам сервера.")
    async def top7_author_stat(self, ctx: discord.ApplicationContext, year: int, month: int):
        logging.info("the /author_stat was used")
        moder = await func.moder( ctx)
        
        if moder == True:
            await ctx.respond("Обработка...")
            logging.debug("top7_author_stat: get hist for author")
            loop = asyncio.get_event_loop()
            resp = await stats.get_author_stat(year=year, mounth=month, loop=loop)
            if resp == None:
                await ctx.send("Ничего не найдено.")
            else:
                await ctx.send(file=discord.File(resp, filename='author_stat.png'))
        else:
            await ctx.respond("У вас нет прав на выполнение данной команды!")



    # Статистика сообщений за месяц
    @discord.slash_command(description="Статистика сообщений за месяц по дням.")
    async def month_statistic(self, ctx: discord.ApplicationContext, year: int, month: int):
        logging.info("the /month_statistic was used")
        moder = await func.moder(ctx)
        if moder == True:
            await ctx.respond("Обработка...")
            logging.debug("month_statistic: get hist for month")
            loop = asyncio.get_event_loop()
            resp = await stats.get_count_hist_for_mouth(month, year, loop=loop)
            if resp == None:
                await ctx.send("Ничего не найдено.")
            else:
                await ctx.send(file=discord.File(resp, filename='hist_for_mouth.png'))
        else:
            await ctx.respond("У вас нет прав на выполнение данной команды!")


    @discord.slash_command(description="Статистика распределения сообщей по каналам сервера за месяц.")
    async def channel_statistics(self, ctx: discord.ApplicationContext, year: int, month: int):
        logging.info("the /channel_statistics was used")
        moder = await func.moder(ctx)
        if moder == True:
            await ctx.respond("Обработка...")
            logging.debug("channel_statistic: get channel statistic")
            loop = asyncio.get_event_loop()
            resp = await stats.get_channels_statistic(month, year, loop=loop)
            if resp == None:
                await ctx.respond("Ничего не найдено.")
            else:
                await ctx.send(file=discord.File(resp, filename='hist_for_mouth.png'))
        else:
            await ctx.respond("У вас нет прав на выполнение данной команды!")

def setup(bot):
    bot.add_cog(Charts(bot)) 