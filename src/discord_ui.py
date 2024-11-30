from discord import ui
import discord
from othr_func import moder_for_user
import dswarn
from datetime import timedelta
import asyncio
from translate import Translator


# Модальный диалог добавления варна
class AddWarnModal(ui.Modal):
    def __init__(self, people: discord.Member, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.people = people
        self.name = people.name
        self.ids = people.id
        self.add_item(ui.InputText(label="Причина", style=discord.InputTextStyle.multiline))

    async def callback(self, interaction: discord.Interaction):
        if await moder_for_user(interaction.user) == True:
            reason = self.children[0].value
            loop = asyncio.get_event_loop()
            resp = await dswarn.add_warn(user_id=self.ids, user_name=self.name, reason=reason, loop=loop)

            embed = discord.Embed(title="GIVE WARN!", description=f"{resp}", color=discord.Color.yellow())
            result = await dswarn.warn_system(self.ids, loop=loop)
            if result == 100:
                await self.people.timeout_for(timedelta(minutes=20))
            elif result == 105:
                await self.people.timeout_for(timedelta(hours=6))
            elif result == 200:
                await self.people.timeout_for(reason="16 предупреждений")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="ERROR!", color=discord.Color.red())
            interaction.response.send_message(embed=embed)


# Выбор цели
class TargetSelectView(discord.ui.View):
    @discord.ui.mentionable_select(placeholder="Выбери пользователя для предупреждения.")
    async def select_callback(self, select, interaction: discord.Interaction): # the function called when the user is done selecting options
        if await moder_for_user(interaction.user) == True:
            await interaction.message.delete()
            people = select.values[0]

            await interaction.response.send_modal(AddWarnModal(title="Reason",people=people))
        else:
            pass
            


class AllUserWarns(discord.ui.View):
    def __init__(self, warn_id):
        super().__init__()
        self.warn_id = warn_id

    @discord.ui.button(label="Удалить!", style=discord.ButtonStyle.danger, emoji="🗑")
    async def button_callback(self, button, interaction: discord.Interaction):
        if await moder_for_user(interaction.user) == True:
            loop = asyncio.get_event_loop()
            await interaction.message.delete()
            await dswarn.delete_warn(self.warn_id, loop=loop)        
        else:
            pass



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