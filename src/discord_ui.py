from discord import ui
import discord
from othr_func import moder_for_user
import dswarn
from datetime import timedelta


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
            resp = dswarn.add_warn(user_id=self.ids, user_name=self.name, reason=reason)

            embed = discord.Embed(title="GIVE WARN!", description=f"{resp}", color=discord.Color.yellow())
            result = await dswarn.warn_system(self.ids)
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


class TargetSelectView(discord.ui.View):
    @discord.ui.mentionable_select(placeholder="Выбери пользователя для предупреждения.")
    async def select_callback(self, select, interaction: discord.Interaction): # the function called when the user is done selecting options
        if await moder_for_user(interaction.user) == True:
            await interaction.message.delete()
            people = select.values[0]

            await interaction.response.send_modal(AddWarnModal(title="Reason",people=people))
        else:
            await interaction.message.delete()



        


