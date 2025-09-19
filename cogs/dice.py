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

async def rollfunc(ctx, userdot=int, mindot=int, maxdot=int, numdice=int, coalnum=int, multi=int, nearmulti=float):
    diceemoji = ["<:diceone:1398193186673000489> ",
                    "<:dicetwo:1398193195573186641> ",
                     "<:dicethree:1398193193039954022> ",
                     "<:dicefour:1398193183334338670> ",
                     "<:dicefive:1398193180310245467> ",
                     "<:dicesix:1398193189659218052> "
                ]
    count = 0
    text = ""
    sumall = []
    if userdot > maxdot and  userdot < mindot:
        await ctx.defer(ephemeral=False)
        await ctx.reply(f"Dot counting must less than {maxdot} and greater than {mindot}", mention_author=False)
    else:
        embed1 = discord.Embed(title="Rolling...", description="<a:dicerolling:1398118137110724799>"*numdice)
        await ctx.defer(ephemeral=False)
        rolling =  await ctx.reply(embed=embed1, mention_author=False)
        await asyncio.sleep(5)
        while count < numdice:
            dice = random.randint(1,6)
            text = text + f"{diceemoji[dice - 1]}"
            sumall.append(dice)
            count += 1
        result = text + f" = {sum(sumall)}"
        if userdot == sum(sumall):
            collection.update_one(
            {"name": ctx.author.name},
            {"$inc":{"coal": int(round(coalnum*multi))}}
            )
            result = result + f"\n\n*You got* `{num_format(int(round(coalnum*multi)))}` *coals for dicing, Congratulations!*"
        elif userdot == sum(sumall) - 1 or userdot == sum(sumall) + 1:
            collection.update_one(
            {"name": ctx.author.name},
            {"$inc":{"coal": int(round(coalnum*nearmulti))}}
            )
            result = result + f"\n\n*You got* `{num_format(int(round(coalnum*nearmulti)))}` *coals for dicing. Cool, even not guess it right*"
        else:
            collection.update_one(
                {"name": ctx.author.name},
                {"$inc":{"coal": int(round(-coalnum*multi))}}
                )
            result = result + f"\n\n*You lost* `{num_format(int(round(coalnum*multi)))}` *coals for dicing. Nice try and better luck next time...*"
        embed2 = discord.Embed(title="Rolled", description=result)
        await rolling.edit(embed=embed2)



class DiceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dice", description="Roll a dice, guess to win or lost")
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dice(self, ctx, number_of_dice: int, number_of_dot: int, amount_of_coal:int):
        doc = collection.find_one({"user_id": ctx.author.id})
        if amount_of_coal < 500:
            await ctx.defer(ephemeral=False)
            await ctx.reply("Required equal or more than 500 coals", mention_author=False)
        elif doc['coal'] < amount_of_coal*number_of_dice:
            await ctx.send('Not enough coals to bet')
        else:
            if number_of_dice == 1:
                await rollfunc(ctx=ctx, userdot=number_of_dot, maxdot=6, mindot=1, numdice=1, coalnum=amount_of_coal, multi=1, nearmulti=0.25)
            elif number_of_dice == 2:
                await rollfunc(ctx=ctx, userdot=number_of_dot, maxdot=12, mindot=1, numdice=2, coalnum=amount_of_coal, multi=2, nearmulti=0.5)
            elif number_of_dice == 3:
                await rollfunc(ctx=ctx, userdot=number_of_dot, maxdot=18, mindot=1, numdice=3, coalnum=amount_of_coal, multi=3, nearmulti=0.75)
            elif number_of_dice > 3:
                await ctx.defer(ephemeral=False)
                await ctx.reply("Max dices is 3", mention_author=False)
            elif number_of_dice < 1:
                await ctx.defer(ephemeral=False)
                await ctx.send("Min dices is 1", mention_author=False)
            else:
                await ctx.defer(ephemeral=False)
                await ctx.send("Invaild command!", mention_author=False)

async def setup(bot):
    await bot.add_cog(DiceCommand(bot))