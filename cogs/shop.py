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

shopitems = [
            {"name": "Fire Sword", "price": 17500, "emoji": "<:firesword:1399707091203133440>","desc":'"The sword alaways shines and cover with red fire"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Fire Dash": 10, "Fire Slash": "unlock at level 5", "Fire Crescent": "unlock at level 10", "Quindurple Flames": "unlock at level 20"}, "type":"sword", "status":"good", "wexp":0, "wexpmax": 100, "lvl": 1}},
            {"name": "Ice Sword", "price": 17500,"emoji": "<:icesword:1399707088455729203>","desc":'"Frozen sword will make you cool down"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Ice Smash": 9, "Ice Spin": "unlock at level 5", "Frozen Slash": "unlock at level 10", "Absolute Zero": "unlock at level 20"}, "type":"sword", "status":"good",  "wexp":0, "wexpmax": 100, "lvl": 1}},
            {"name": "Saber", "price": 20000,"emoji": "<:saber:1399707076032336033>","desc":'"Slash!"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Saber Slash": 12, "Saber Circles": "unlock at level 12", "Enchance": "unlock at level 20", "Deadly Cuts": "Unlock at lvl 30"}, "type":"sword", "status":"good",  "wexp":0, "wexpmax": 100, "lvl": 1}},
            {"name": "Katana", "price": 10000,"emoji": "<:katana:1399707094755573850>","desc":'"The sword which designed by Japanese"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Rush Cut": 7.5, "Muitiple Cuts": 7.5*3}, "type":"sword", "status":"good",  "wexp":0, "wexpmax": 100, "lvl": 1}},
            {"name": "Shuriken X50", "price": 4500,"emoji": "<:shuriken:1400454245014311022>","desc":"","priceicon":"<:charcoal:1400474440579682508>","info":{"ability":["Throw 1", "Throw 3", 3], "type":"Throwable Weapon", "amount": 50}},
            {"name": "Kunai x50", "price": 5000,"emoji": "<:kunai:1400453962284662867>","desc":"","priceicon":"<:charcoal:1400474440579682508>","info":{"ability":["Throw 1", "Throw 3", 3.5], "type":"Throwable Weapon", "amount": 50}},
            {"name": "Electric Sword", "price": 17500,"emoji": "<:electricsword:1399707080612384838>","desc":'"A fast and rumbled sword"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Electric Flash": 10, "Bolt Smash": "unlock at level 6", "Thunder Slash": "unlock at lvl 12", "Death Thunder": "unlock at lvl 25"}, "type":"sword", "status":"good",  "wexp":0, "wexpmax": 100, "lvl": 1}},
            {"name": "Dragon Fan", "price": 30000,"emoji": "<:dragonfan:1399707104545341510>","desc":'"The dragon will blows wind"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Wind Blow": 3, "Dragon Slash": "unlock at level 12", "Wind Storm": "unlock at level 24", "Dragons Chaos": "unlock at level 36"}, "type":"sword", "status":"good",  "wexp":0, "wexpmax": 100, "lvl": 1}},
            {"name": "Heavy Sword", "price": 7500,"emoji": "<:heavysword:1399707086161444874>","desc":'"Decent Damage, cheap"',"priceicon":"<:charcoal:1400474440579682508>","info":{"durability": 100, "ability":{"Swings": 9, "Spin": 9}, "type":"sword", "status":"good",  "wexp":0, "wexpmax": 100, "lvl": 1}}
    ]
shopfood = [
            {"name": "Rice", "price": 500, "emoji": "<:rice:1405190334173937696>","desc":"The food which people always need","priceicon":"<:yen:1405359772206895115>","info":{"type":"food", "energy":100, "amount": 1}},
            {"name": "Udon", "price": 750,"emoji": "<:udon:1405190341841391689>","desc":"Boost 150 HP after battle","priceicon":"<:yen:1405359772206895115>","info":{"type":"food", "health":150, "amount": 1}},
            {"name": "Fried Egg", "price": 250,"emoji": "<:fried_egg:1405190337680638113>","desc":"","priceicon":"<:yen:1405359772206895115>","info":{"type":"food", "energy":50, "amount": 1}},
            {"name": "Beef Steak", "price": 1000,"emoji": "<:steak:1405190349701255319>","desc":"Boost 100","priceicon":"<:yen:1405359772206895115>","info":{"type":"food", "health":250, "amount": 1}}
        ]
shopitems = sorted(shopitems, key=lambda shopitems: shopitems["price"])
shopfood = sorted(shopfood, key=lambda shopfood: shopfood["price"])

class ShopView(discord.ui.View):
    def __init__(self, items, id):
        super().__init__(timeout=60)
        self.items = items
        self.id = id
        self.page = 0
        self.per_page = 5
        self.update_buttons()
    
    def update_buttons(self):
        self.clear_items()

        start = self.page * self.per_page
        end = start + self.per_page
        current_items = self.items[start:end]

        options = []
        for item in current_items:
            if item['priceicon'] == "<:charcoal:1400474440579682508>":
                options.append(discord.SelectOption(label=f"{item['name']} - {num_format(item['price'])} coals",description=f"{item['desc']}", emoji=item['emoji']))
            elif item['priceicon'] == "<:yen:1405359772206895115>":
                options.append(discord.SelectOption(label=f"{item['name']} - {num_format(item['price'])} yen",description=f"{item['desc']}", emoji=item['emoji']))
        self.add_item(ShopItemSelection(options))


        if self.page > 0:
            self.add_item(PrevButton())
        else:
            self.add_item(DisabledPrevButton())
        
        if self.items == shopfood:
            self.add_item(ShopWeapon())
        if self.items == shopitems:
            self.add_item(ShopFood())

        if end < len(self.items):
            self.add_item(NextButton())
        else:
            self.add_item(DisabledNextButton())

class ShopItemSelection(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Select an item to buy", min_values=1, max_values=1, options=options)



    async def interaction_check(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if interaction.user.id != view.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        selected_label = self.values[0]

        splited_label = selected_label.split(" - ")
        price = splited_label[1].split()
        if price[1] == "coals":
            priceicon = "<:charcoal:1400474440579682508>"
        elif price[1] == "yen":
            priceicon = "<:yen:1405359772206895115>"
        view = self.view 
        
        final_view = ChoicesToBuy(name=splited_label[0], id=interaction.user.id, price=num_unformat((price[0])), items=view.items, page=view.page, icon=priceicon)
        embed = discord.Embed(title="Shop", description=f"You selected: **{splited_label[0]}**\nPrice: `{price[0]}`{priceicon}, Buy?")
        await interaction.response.edit_message(embed=embed, view=final_view)

def generate_shop_embed(items, page, per_page):
    start = page * per_page
    end = start + per_page
    if len(items) // per_page == len(items) / per_page:
        totalpage = len(items) // per_page
    elif len(items) / per_page > len(items) // per_page:
        totalpage = len(items) // per_page + 1
    embed = discord.Embed(title="🛒 Shop", description=f"Page {page + 1} of {totalpage}")
    for item in items[start:end]:
        embed.add_field(name=f"{item['emoji']} • {item['name']}", value=f"Price: {format(item['price'])} {item['priceicon']}", inline=False)
    return embed

class ChoicesToBuy(discord.ui.View):
    def __init__(self, name, id, price, items, page, icon):
        super().__init__(timeout=60)
        self.name = name
        self.id = id
        self.price = price
        self.items = items
        self.page = page
        self.icon = icon

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            userinfo = collection.find_one({"user_id": self.id})
            if self.icon == "<:charcoal:1400474440579682508>":
                bank = userinfo["coal"]
            elif self.icon == "<:yen:1405359772206895115>":
                bank = userinfo['yen']
            if bank < self.price:
                embed = discord.Embed(
                    title="Purchased failed",
                    description=f"You don't have enough coal to buy item!",
                    color=discord.Colour.red()
                )
                self.clear_items()
                self.add_item(BackToShop())
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                items_in_users_inv = []
                if userinfo["inv"] != []:
                    for name in userinfo["inv"]:
                        items_in_users_inv.append(name["name"])
                for i in self.items:
                    if self.name == i["name"]:
                        if i["info"]["type"] == "sword":
                            item = {"name": self.name, "emoji": i["emoji"]}
                            item.update(i["info"])
                            collection.update_one(
                                {"user_id": self.id},
                                {"$push": {"inv": item}}
                            )
                            break
                        elif i["info"]["type"] == "Throwable Weapon":
                            if self.name[:-4] in items_in_users_inv:
                                itembought = userinfo["inv"][items_in_users_inv.index(self.name[:-4])]
                                collection.update_one(
                                    {"user_id": self.id},
                                    {"$pull": {"inv": itembought}}
                                )
                                itembought.update({"amount": itembought["amount"] + 50})
                                collection.update_one(
                                    {"user_id": self.id},
                                    {"$push": {"inv": itembought}}
                                )
                            elif self.name[:-4] not in items_in_users_inv:
                                item = {"name": self.name[:-4], "emoji": i["emoji"]}
                                item.update(i["info"])
                                collection.update_one(
                                    {"user_id": self.id},
                                    {"$push": {"inv": item}}
                                )
                                break
                        elif i["info"]["type"] == "food":
                            if self.name in items_in_users_inv:
                                itembought = userinfo["inv"][items_in_users_inv.index(self.name)]
                                collection.update_one(
                                    {"user_id": self.id},
                                    {"$pull": {"inv": itembought}}
                                )
                                itembought.update({"amount": itembought["amount"] + i["info"]["amount"]})
                                collection.update_one(
                                    {"user_id": self.id},
                                    {"$push": {"inv": itembought}}
                                )
                            elif self.name not in items_in_users_inv:
                                item = {"name": self.name, "emoji": i["emoji"]}
                                item.update(i["info"])
                                collection.update_one(
                                    {"user_id": self.id},
                                    {"$push": {"inv": item}}
                                )
                                break
                embed = discord.Embed(
                    title="Purchased completed",
                    description=f"You purchased {self.name}!",
                    color=discord.Colour.brand_green()
                )
                self.clear_items()
                self.add_item(BackToShop())
                await interaction.response.edit_message(embed=embed, view=self)
        except Exception:
            traceback.print_exc()

    @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            view = ShopView(self.items,self.id)
            embed = generate_shop_embed(self.items ,0, 5)
            await interaction.response.edit_message(embed=embed,view=view)
        except Exception as e:
            print(e)



class PrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.gray)

    async def interaction_check(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if interaction.user.id != view.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view
        view.page -= 1
        view.update_buttons()
        embed = generate_shop_embed(view.items, view.page, view.per_page)
        await interaction.response.edit_message(embed=embed, view=view)

class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➡️ Next", style=discord.ButtonStyle.gray)

    async def interaction_check(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if interaction.user.id != view.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view
        view.page += 1
        view.update_buttons()
        embed = generate_shop_embed(view.items, view.page, view.per_page)
        await interaction.response.edit_message(embed=embed, view=view)

class BackToShop(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Back to shop", style=discord.ButtonStyle.gray)

    async def interaction_check(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if interaction.user.id != view.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        confirm_view: ChoicesToBuy = self.view
        shop_view = ShopView(confirm_view.items, confirm_view.id)
        shop_view.page = confirm_view.page
        shop_view.update_buttons()
        embed = generate_shop_embed(shop_view.items, shop_view.page, shop_view.per_page)
        await interaction.response.edit_message(embed=embed, view=shop_view)

class ShopFood(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Food", style=discord.ButtonStyle.gray)

    async def interaction_check(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if interaction.user.id != view.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        try:
            view: ShopView = self.view
            view.clear_items()
            anotherview = ShopView(items=shopfood, id=view.id)
            embed = generate_shop_embed(items=shopfood, page=0, per_page=5)
            await interaction.response.edit_message(embed=embed, view=anotherview)
        except Exception as e:
            print(e)

class ShopWeapon(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Weapon", style=discord.ButtonStyle.gray)

    async def interaction_check(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if interaction.user.id != view.id:
            await interaction.response.send_message("You are not the one who invoked this command.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        try:
            view: ShopView = self.view
            view.clear_items()
            anotherview = ShopView(items=shopitems, id=view.id)
            embed = generate_shop_embed(items=shopitems, page=0, per_page=5)
            await interaction.response.edit_message(embed=embed, view=anotherview)
        except Exception as e:
            print(e)

class DisabledPrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.gray, disabled=True)

class DisabledNextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="➡️ Next", style=discord.ButtonStyle.gray, disabled=True)




class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx):
        try:
            view = ShopView(shopitems, ctx.author.id)
            embed = generate_shop_embed(shopitems, 0, 5)
            await ctx.reply(embed=embed, mention_author=False, view=view)
        except Exception:
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))