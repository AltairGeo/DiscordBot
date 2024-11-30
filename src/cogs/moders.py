from discord.ext import commands
import discord
from log import logging
import dswarn
import config
import asyncio
from datetime import timedelta
import othr_func as func
import discord_ui as uui


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    Moders = discord.SlashCommandGroup("mod", "Команды для модерирования.")

    @Moders.command(description="Дать предупреждение пользователю.")
    async def addwarn(self, ctx: discord.ApplicationContext):
        if await func.moder(ctx=ctx):
            await ctx.respond("Выбор пользователя:", view=uui.TargetSelectView())
        else:
            await ctx.respond("У вас нет прав на выполнение данной команды!")


    # Дать предупреждение
    @Moders.command(description="Дать предупреждение пользователю(Устаревший интерфейс).")
    async def addwarn_legacy(self, ctx: discord.ApplicationContext, name: discord.Member, reason: str):
        logging.info("the /addwarn was used")
        loop = asyncio.get_event_loop()
        author_roles = ctx.author.roles
        mod = config.MOD_ID
        right = 0
        for i in author_roles:
            i = i.id
            if str(i) == mod:
                user_id = name.id
                user_name = name.name 
                await ctx.respond(await dswarn.add_warn(user_id, user_name, reason, loop))
                logging.debug(f"Add warn to {user_name} for reason: {reason}")
                result = await dswarn.warn_system(user_id, loop=loop)
                if result == 100:
                    await name.timeout_for(timedelta(minutes=20))
                elif result == 105:
                    await name.timeout_for(timedelta(hours=6))
                elif result == 200:
                    await name.timeout_for(reason="16 предупреждений")
                right = 1
        if right == 0:
            await ctx.respond("У вас нет прав на выполнение данной команды!")

    


    @Moders.command(description="Удалить предупреждение у пользователя по id(Устаревший интерфейс).")
    async def delwarn_legacy(self, ctx, id_warn: int):
        loop = asyncio.get_event_loop()
        logging.info("the /delwarn was used")
        author_roles = ctx.author.roles
        mod = config.MOD_ID
        right = 0
        for i in author_roles:
            i = i.id
            if str(i) == mod:
                await ctx.respond("Обработка...")
                await ctx.send(await dswarn.delete_warn(id_warn, loop=loop))
                logging.debug(f"Deleted warning with id = {id_warn}")
                right = 1
        if right == 0:
            await ctx.respond("У вас нет прав на выполнение данной команды!")


    # Все предупреждения пользователя
    @Moders.command(description="Показать все предупреждения пользователя.")
    async def alluserwarn(self, ctx: discord.ApplicationContext, name: discord.Member):
        logging.info("the /alluserwarn was used")
        ListOfMessage = []
        if await func.moder(ctx):
            await ctx.respond("Обработка!")
            loop = asyncio.get_event_loop()
            for i in await dswarn.all_user_warn(name.id, loop=loop):
                embed = discord.Embed(title=f"{i[2]}", description=f"Причина: {i[3]}", color=discord.Color.dark_green())
                embed.set_footer(text=f"warn_id: {i[0]}")
                ListOfMessage.append(await ctx.send(embed=embed, view=uui.AllUserWarns(i[0])))
            await asyncio.sleep(60)
            for i in ListOfMessage:
                try:
                    await i.delete()
                except Exception as e:
                    logging.error(f"alluserwarn delete messages was crush! With error:{e}")
        else:
            await ctx.send("У вас нет прав на выполнение данной команды!")


    # мут
    @Moders.command(description="Дать мут на определённое кол-во часов.")
    async def mute(self, ctx: discord.ApplicationContext, name: discord.Member, hours: int):
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

def setup(bot):
    bot.add_cog(moderation(bot))