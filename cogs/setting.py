import discord
import random
import pymongo
import asyncio
from pymongo import MongoClient
from discord.ext import commands
import datetime
from secret import mongotoken

client = MongoClient(mongotoken)


db = client["Playerlist"]
collection = db["players"]


class SettingView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=300)
        self.info = collection.find_one({"user_id": uid})
        self.uid = uid
        self.update()

    def update(self):
        self.clear_items()
        if self.info["mine_notification"] == "ON":
            a = 'off'
        elif self.info["mine_notification"] == "OFF":
            a = 'on'
        option = [discord.SelectOption(label=f"Mine Notification: {self.info['mine_notification']}", description=f"Toggle to turn {a}")]
        self.add_item(ToggleSetting(option))


class ToggleSetting(discord.ui.Select):
    def __init__(self, option):
        super().__init__(placeholder="Toggle...", min_values=1, max_values=1, options=option)
     
    async def callback(self, interaction: discord.Interaction):
        view: SettingView = self.view
        selected_label = self.values[0]

        splited_label = selected_label.split()
        settingname = f"{splited_label[0]}" + " " + f"{splited_label[1]}"
        toggle = splited_label[2]
        if toggle == "ON":
            collection.update_one(
                {"user_id": view.uid},
                {"$set":{"mine_notification": "OFF", "req_to_notify": "OFF"}}
                )         
            view.info = collection.find_one({"user_id": view.uid})
            embed = discord.Embed(title="Settings", description=f"***Mining cooldown notification:*** ***`{view.info['mine_notification']}`***")
            embed.set_footer(text=f"Complete setting {settingname} turned off")
        elif toggle == "OFF":
            collection.update_one(
                {"user_id": view.uid},
                {"$set":{"mine_notification": "ON"}}
                )         
            view.info = collection.find_one({"user_id": view.uid})
            embed = discord.Embed(title="Settings", description=f"***Mining cooldown notification:*** ***`{view.info['mine_notification']}`***")
            embed.set_footer(text=f"Complete setting {settingname} turned on")
        view.update()

        
        await interaction.response.edit_message(embed=embed, view=view)

class Setting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bg_task = None

    async def cooldown_notification(self):
        await self.bot.wait_until_ready()
        while True:
            alluserinfo = list(collection.find())
            for i in alluserinfo:
                if datetime.datetime.now().timestamp() >= i['cdownmine'] and i['req_to_notify'] == "ON":
                    collection.update_one(
                        {"user_id": i["user_id"]},
                        {"$set":{"req_to_notify":"OFF"}}
                        )
                    user = await self.bot.fetch_user(i["user_id"])
                    await user.send("You can mine again")
            await asyncio.sleep(5)

    async def cog_load(self):
        self.bg_task = asyncio.create_task(self.cooldown_notification())

    @commands.command()
    async def setting(self, ctx):
        try:
            userinfo = collection.find_one({"user_id": ctx.author.id})
            embed = discord.Embed(title="Settings", description=f"***Mining cooldown notification:*** ***`{userinfo['mine_notification']}`***")
            embed.set_footer(text="Toggle to turn on/off")
            view = SettingView(uid=ctx.author.id)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(e)
        
async def setup(bot):
    await bot.add_cog(Setting(bot))