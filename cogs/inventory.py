import discord
import random
import pymongo
import asyncio
from pymongo import MongoClient
from discord.ext import commands
import datetime
from time import gmtime, strftime
import traceback
from format import num_format,num_unformat
from secret import mongotoken

client = MongoClient(mongotoken)


db = client["Playerlist"]
collection = db["players"]

def generate_inv_embed(items:list, page:int, per_page:int, name:str):
    start = page * per_page
    end = start + per_page
    if len(items) // per_page == len(items) / per_page:
        totalpage = len(items) // per_page
    elif len(items) / per_page > len(items) // per_page:
        totalpage = len(items) // per_page + 1
    text = ""
    barstart = 0
    barend = 0.1
        
            
    progressbar = ["△▽△▽△▽△▽△▽",
                    "▲▽△▽△▽△▽△▽",
                    "▲▼△▽△▽△▽△▽",
                    "▲▼▲▽△▽△▽△▽",
                    "▲▼▲▼△▽△▽△▽",
                    "▲▼▲▼▲▽△▽△▽",
                    "▲▼▲▼▲▼△▽△▽",
                    "▲▼▲▼▲▼▲▽△▽",
                    "▲▼▲▼▲▼▲▼△▽",
                    "▲▼▲▼▲▼▲▼▲▽"
                    ]
    for iteminfo in items[start:end]:
        if iteminfo["type"] == "sword":
            text = text + f"{iteminfo['emoji']} | ***{iteminfo['name']}:***"
            for bar in range(len(progressbar)):
                if iteminfo['wexp']/iteminfo['wexpmax'] >= barstart and iteminfo['wexp']/iteminfo['wexpmax'] < barend:
                    text = text + f" ***/***{progressbar[bar]}***/***"
                    break
                else:
                    barstart += 0.1
                    barend += 0.1
            text = text + f" ***`{iteminfo['wexp']}/{iteminfo['wexpmax']}`***\n"
        elif iteminfo["type"] == "Throwable Weapon" or iteminfo["type"] == "food":
            text = text + f"{iteminfo['emoji']} | ***{iteminfo['name']}: `x{iteminfo['amount']}`***\n"
    embed = discord.Embed(title=f"{name}'s Inventory:", description=text)
    embed.set_footer(text=f"Corecoal | Page {page + 1} of {totalpage}")  
    return embed

class InventoryView(discord.ui.View):
    def __init__(self, invitems:list, id:int, listtype:list):
        super().__init__(timeout=60)
        self.invitems = invitems
        self.id = id
        self.page = 0
        self.per_page = 5
        self.listtype = listtype
        self.update()

    def update(self):
        self.clear_items()
        start = self.page * self.per_page
        end = start + self.per_page
        for item in self.invitems[start:end]:
            self.add_item(InventoryButton(item['name'], item['emoji'], item, uid=self.id))


        category = [
                discord.SelectOption(label="Sword"),
                discord.SelectOption(label="Throwable Weapon"),
                discord.SelectOption(label="Food"),
                ]
        if self.listtype == []:
            self.add_item(DisabledISAB())
            self.add_item(InventorySort(category))
        elif self.listtype != []:
            if "Sword" in self.listtype:
                category.pop(0)
                category.insert(0, discord.SelectOption(label="Sword", default=True))
            if "Throwable Weapon" in self.listtype:
                category.pop(1)
                category.insert(1, discord.SelectOption(label="Throwable Weapon", default=True))
            if "Food" in self.listtype:
                category.pop(2)
                category.insert(2, discord.SelectOption(label="Food", default=True))
            self.add_item(InvShowAllButton())
            self.add_item(InventorySort(category))





            
class InventorySort(discord.ui.Select):
    def __init__(self, category):
        super().__init__(placeholder="Sort...", max_values=3, min_values=1, options=category)

    async def callback(self, interaction: discord.Interaction):
        listitemaftercategories = []
        types = []
        if "Sword" in self.values:
            types.append("sword")
        if "Throwable Weapon" in self.values:
            types.append("Throwable Weapon")
        if "Food" in self.values:
            types.append("food")

        userinfo = collection.find_one({"user_id": interaction.user.id})
        if self.values != []:
            for atype in types:
                for item in userinfo["inv"]:
                    if item['type'] == atype:
                        listitemaftercategories.append(item)

        view = InventoryView(listitemaftercategories, interaction.user.id, self.values)
        embed = generate_inv_embed(items=listitemaftercategories, page=0, per_page=5, name=userinfo["name"])
        await interaction.response.edit_message(embed=embed, view=view)



class InventoryButton(discord.ui.Button):
    def __init__(self, name, emoji, item, uid):
        super().__init__(label=name ,emoji=emoji)
        self.item = item
        self.name = name
        self.emoji = emoji  
        self.uid = uid     
    async def callback(self, interaction: discord.Interaction):  
        embed = discord.Embed(title=f"{interaction.user.display_name}'s {self.name}")      
        if self.item["type"] == "sword":
            abilitytext = ""
            for ability in self.item["ability"]:
                for name, info in ability.item():
                    if type(info) == int:
                        abilitytext = abilitytext + f"|{name}| DMG: {info}\n"
                    elif type(info) == str:
                        abilitytext = abilitytext + f"{info}\n"
            embed.add_field(name="Ability", value=abilitytext)
            embed.add_field(name="", value=f"**Durability**\n*{self.item['durability']}*\n**Level {self.item['lvl']}**\n*{self.item['wexp']}/{self.item['wexpmax']}*", inline=True)
        elif self.item["type"] == "Throwable Weapon":
            embed.add_field(name="", value=f"**Damage per {self.item['name'].lower()}**\n{self.item['ability'][2]}")
            userinfo = collection.find_one({"user_id": interaction.user.id})
            arctext = ""
            for bodypart,precent in userinfo['TW Accuracy'].item():
                arctext = arctext + f"*{bodypart}: {precent*100}*\n"
            embed.add_field(name="", value=f"**Accuracy (increase by user's level)**\n{arctext}")
        elif self.item["type"] == "food":
            embed.add_field(name="", value=f"**Health boost**\n{self.item['ability'][2]}")
            embed.add_field(name="", value=f"**Accuracy (increase by user's level)**\n{arctext}")
        await interaction.response.edit_message(embed=embed, view=ItemView(self.item, self.uid))
        

class ItemView(discord.ui.View):
    def __init__(self, item, uid):
        self.item = item
        self.uid = uid
        self.clear_items()
        
        userinfo = collection.find_one({"user_id": self.uid})
        if self.item["type"] == "sword" or self.item["type"] == "Throwable Weapon":
            if self.item["type"] == "sword":
                if self.item['wexp']/self.item['wexpmax'] == 1 and self.item['lvl']%5 == 0:
                    self.add_item(UpgradeButton())
                else:
                    self.add_item(DisabledUpgradeButton())
            if self.item in userinfo['invequipped']:
                self.add_item(Unequip())
            elif self.item not in userinfo['invequipped']:
                self.add_item(Equip())
        elif self.item["type"] == "food":
            self.add_item(Eat())
        
        


class InvShowAllButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✘ Show All (unsort)", style= discord.ButtonStyle.red, row=2)
       
    async def callback(self, interaction: discord.Interaction):
        userinfo = collection.find_one({"user_id": interaction.user.id})                
        embed = generate_inv_embed(items=userinfo["inv"], page=0, per_page=5, name=userinfo["name"])
        await interaction.response.edit_message(embed=embed, view=InventoryView(userinfo["inv"], interaction.user.id,[]))

class DisabledISAB(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✘ Show All (unsort)", style= discord.ButtonStyle.red, disabled=True, row=2)

class UpgradeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Upgrade for 1 crystal", style=discord.ButtonStyle.gray)

class DisabledUpgradeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Upgrade for 1 crystal", style=discord.ButtonStyle.gray, disabled=True)

class Equip(discord.ui.Button):
    def __init__(self, item):
        super().__init__(label="Equip", style=discord.ButtonStyle.gray)
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        userinfo = collection.find_one({"user_id": interaction.user.id})
        text = ""
        barstart = 0
        barend = 0.1
            
        progressbar = ["△▽△▽△▽△▽△▽",
                        "▲▽△▽△▽△▽△▽",
                        "▲▼△▽△▽△▽△▽",
                        "▲▼▲▽△▽△▽△▽",
                        "▲▼▲▼△▽△▽△▽",
                        "▲▼▲▼▲▽△▽△▽",
                        "▲▼▲▼▲▼△▽△▽",
                        "▲▼▲▼▲▼▲▽△▽",
                        "▲▼▲▼▲▼▲▼△▽",
                        "▲▼▲▼▲▼▲▼▲▽"
                        ]
        for iteminfo in userinfo['invequipped']:
            count += 1
            if iteminfo["type"] == "sword":
                text = text + f"{iteminfo['emoji']} | ***{iteminfo['name']}:***"
                for bar in range(len(progressbar)):
                    if iteminfo['wexp']/iteminfo['wexpmax'] >= barstart and iteminfo['wexp']/iteminfo['wexpmax'] < barend:
                        text = text + f" ***/***{progressbar[bar]}***/***"
                        break
                    else:
                        barstart += 0.1
                        barend += 0.1
                text = text + f" ***`{iteminfo['wexp']}/{iteminfo['wexpmax']}`***\n"
            elif iteminfo["type"] == "Throwable Weapon":
                text = text + f"{iteminfo['emoji']} | ***{iteminfo['name']}: `x{iteminfo['amount']}`***\n"
        


class Unequip(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Unequip", style=discord.ButtonStyle.gray)


class Eat(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Eat", style=discord.ButtonStyle.gray)

class SlotsView(discord.ui.View):
    def __init__(self, item, equipments):
        self.item = item
        self.equipments = equipments
        self.clear_items()

        count = 0
        if self.item["type"] == "sword":
            for equipment in self.equipments:
                if type(equipment) == int:
                    if equipment == 0:
                        self.add_item(SlotButton(name="Melee (empty)", emoji=None, TF=False, customid=count, item=self.item))
                    elif equipment == 1:
                        self.add_item(SlotButton(name=f"Sword {count} (empty)", emoji=None, TF=True, customid=count, item=self.item))
                        count += 1
                elif type(equipment) == dict:
                    if equipment["type"] == "sword":
                        self.add_item(SlotButton(name=equipment["name"], emoji=equipment["emoji"], TF=True, customid=count, item=self.item))
                    elif equipment["type"] == "Throwable Weapon":
                        self.add_item(SlotButton(name=equipment["name"], emoji=equipment["emoji"], TF=False, customid=count, item=self.item))
                count += 1
        if self.item["type"] == "Throwable Weapon":
            for equipment in self.equipments:
                if type(equipment) == int:
                    if equipment == 0:
                        self.add_item(SlotButton(name="Melee (empty)", emoji=None, TF=True, customid=count, item=self.item))
                    elif equipment == 1:
                        self.add_item(SlotButton(name=f"Sword {count} (empty)", emoji=None, TF=False, customid=count, item=self.item))
                        count += 1
                elif type(equipment) == dict:
                    if equipment["type"] == "sword":
                        self.add_item(SlotButton(name=equipment["name"], emoji=equipment["emoji"], TF=False, customid=count, item=self.item))
                    elif equipment["type"] == "Throwable Weapon":
                        self.add_item(SlotButton(name=equipment["name"], emoji=equipment["emoji"], TF=True, customid=count, item=self.item))
                count += 1

class SlotButton(discord.ui.Button):
    def __init__(self, name, emoji, TF, customid, item):
        super().__init__(label=name, emoji=emoji, disabled=TF, custom_id=customid)
        self.item = item
        self.name = name
        self.emoji = emoji

    async def callback(self, interaction: discord.Interaction):
        userinfo = collection.find_one({"user_id": interaction.user.id})
        collection.update_one
        (
            {"user_id": interaction.user.id},
            {
                "$pull": {"inv": self.item}
            }
        )
        userinfo['invequipped'][self.custom_id] = self.item
        embed = discord.Embed(title=None, description=f"*You equipped {self.emoji} | **{self.name}** in equippment*")
        await interaction.response.edit_message(embed=embed, view=BackToInventoryView())


        
class BackToInventoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.clear_items()

    @discord.ui.button(label="⬅︎", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction):
        userinfo = collection.find_one({"user_id": interaction.user.id})
        view: InventoryView = self.view
        embed = generate_inv_embed(item=userinfo['inv'], page=view.page, per_page=view.per_page, name=interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=InventoryView(invitems=userinfo['inv'], id=interaction.user.id, listtype=view.listtype))

class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="inventory", aliases=["inv"], description="Show user's inventory, upgrades, actions")
    async def inventory(self, ctx):
        userinfo = collection.find_one({"user_id": ctx.author.id})                
        embed = generate_inv_embed(items=userinfo["inv"], page=0, per_page=5, name=ctx.author.name)
        await ctx.defer(ephemeral=False)
        await ctx.reply(embed=embed, view=InventoryView(userinfo["inv"], ctx.author.id,[] ))

async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))