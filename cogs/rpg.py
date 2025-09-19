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




async def levelup(ctx, uid, expgain=int):
    collection.update_one(
        {"user_id": uid},
        {"$inc":{"exp":expgain}}
        )
    user = collection.find_one({"user_id": uid})
    listexpperlvl = user["expmaxperlv"]
    if user["exp"] == listexpperlvl[user["Lv"]-1]:
        collection.update_one(
        {"user_id": uid},
        {"$inc":{"Lv":1}}
        )
        user = collection.find_one({"user_id": uid})
        await ctx.send(f"{ctx.author.mention}, You got leveled up to {user['Lv']}")
        collection.update_one(
        {"user_id": uid},
        {"$push":{"expmaxperlv":int(round((500*(user["Lv"]*100+69)/(1000)+500))+listexpperlvl[user["Lv"]-2])}}
        )



    

class LeaderboardButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15)
        self.all_docs = list(collection.find().sort("coal", pymongo.DESCENDING).limit(50))

    async def show_page(self, interaction: discord.Interaction, a: int, b: int):
        text = ""
        for i in self.all_docs[a:b]:
            text += f"{self.all_docs.index(i)+1}    |    {i['name']}: {i['coal']}\n"
        embed = discord.Embed(title="Leaderboard", description="")
        embed.add_field(name="", value=text, inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="1", style=discord.ButtonStyle.gray)
    async def page1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, 0, 10)

    @discord.ui.button(label="2", style=discord.ButtonStyle.gray)
    async def page2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, 10, 20)

    @discord.ui.button(label="3", style=discord.ButtonStyle.gray)
    async def page3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, 20, 30)

    @discord.ui.button(label="4", style=discord.ButtonStyle.gray)
    async def page4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, 30, 40)

    @discord.ui.button(label="5", style=discord.ButtonStyle.gray)
    async def page5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, 40, 50)


class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        
    @commands.command()
    async def start(self, ctx):
        if collection.find_one({"name": ctx.author.name}) == None:
            collection.insert_one
            (
                {
                    "name": ctx.author.name,
                    "user_id": ctx.author.id,
                    "coal": 0,
                    "inv": [],
                    "energy": 100,
                    "health": 500,
                    "cdownmine": datetime.datetime.now().timestamp(),
                    "Lv": 1,
                    "exp": 0,
                    "expmaxperlv":[500],
                    "req_to_notify":"OFF",
                    "mine_notification":"ON",
                    "yen":0,
                    "invequipped": [0,1,1],
                    "TW Accuracy": {"Head": 0.03, "Body": 0.91, "Legs": 0.06}
                }
            )
            print("New user registered")
            await ctx.send("Registered completed")
        else:
            await ctx.send("You have already registered")


    @commands.command()
    @commands.cooldown(rate=1, per=4, type=commands.BucketType.user)
    async def mine(self, ctx):
        tracker = collection.find_one({"user_id": ctx.author.id})
        if tracker != None:
            if tracker["cdownmine"] <= datetime.datetime.now().timestamp():
                if tracker["energy"] == 0:
                    collection.update_one(
                    {"user_id": ctx.author.id},
                    {"$set":{"energy": 100}}
                    )
                embed = discord.Embed(title="", description="*You are running somewhere to find the some coal...*", colour=discord.Color.light_grey())
                msg = await ctx.reply(embed=embed, mention_author=False)
                await asyncio.sleep(float(random.randint(3,6)))
                commoncoal = random.randint(3,25)
                rarecoal = random.randint(55,100)
                epiccoal = random.randint(225,725)
                mythiccoal = random.randint(1000,2100)
                legendarycoal = random.randint(2800,4000)
                coalnum = [commoncoal,rarecoal,epiccoal,mythiccoal,legendarycoal]
                finalcoal = random.choices(coalnum,weights=[0.65,0.06,0.009,0.0065,0.0038],k=1)[0]
                collection.update_one(
                    {"user_id": ctx.author.id},
                    {"$inc":{"coal":finalcoal, "energy":-1}},
                )
                crystalsrate = random.choices([0,1,2,3],[0.5,0.5,0.025,0.025],k=1)[0]
                crystals = [{"name":"Fire Crystal", "emoji":"<:firecrystal:1412697350727532554>", "amount": crystalsrate},
                           {"name":"Ice Crystal", "emoji":"<:icecrystal:1412697354733359198>", "amount": crystalsrate},
                           {"name":"Electric Crystal", "emoji":"<:electriccrystal:1412697346743205958>", "amount": crystalsrate}]
                crystal = random.choice(crystals)
                text = f"***You found and mined:***\n「<:charcoal:1400474440579682508>」 *`x{num_format(finalcoal)}` coal*"
                if crystal["amount"] != 0:
                    text = text + f"\n「{crystal['emoji']}」 *`x{crystal['amount']}` {crystal['name']}*"
                    listnames = []
                    for item in tracker["inv"]:
                        listnames.append(item['name'])
                    if crystal["name"] not in listnames:                      
                        collection.update_one(
                            {"user_id": ctx.author.id},
                            {"$push": {"inv":crystal}}
                        )
                    elif crystal["name"] in listnames:
                        location = listnames.index(crystal["name"])
                        crystalbefore = tracker["inv"][location]
                        crystalbefore.update({"amount": crystalbefore["amount"]+crystal["amount"]})
                        invafter = tracker["inv"]
                        collection.update_one(
                        {"user_id": ctx.author.id},
                        {"$set": {"inv":invafter}}
                        )

                embed = discord.Embed(title="", description=text, colour=discord.Color.from_rgb(255,255,255))
                await msg.edit(embed=embed)
                await levelup(ctx=ctx, expgain=1, uid=ctx.author.id)
                if tracker["energy"] == 1:
                    unix5min = datetime.datetime.now() + datetime.timedelta(minutes=5)
                    collection.update_one(
                    {"user_id": ctx.author.id},
                    {"$set":{"cdownmine": unix5min.timestamp()}}
                    )
                    if tracker["req_to_notify"] == "OFF" and tracker["mine_notification"] == "ON":
                        collection.update_one(
                        {"user_id": ctx.author.id},
                        {"$set":{"req_to_notify":"ON"}}
                        )
                    embed = discord.Embed(title="Your energy ran out!", description=f"Take a break for 5 minutes, so you can mine again...")
                    await ctx.send(embed=embed)
            elif tracker["cdownmine"] > datetime.datetime.now().timestamp():
                min = strftime("%M", gmtime(tracker["cdownmine"]-datetime.datetime.now().timestamp()))
                sec = strftime("%S", gmtime(tracker["cdownmine"]-datetime.datetime.now().timestamp()))
                embed = discord.Embed(title="Your energy is being recovered...", description=f"You have to take a break in <t:{int(tracker['cdownmine'])}:R> to mine again")
                await ctx.reply(embed=embed, delete_after=int(min)*60+int(sec))
        else:
            await ctx.reply("You must register to use game's command!")
                    
    @commands.command(name="lb",aliases=["leaderboard"])
    async def lb(self, ctx):
        text = ""
        idlist = []
        embed = discord.Embed(title="Leaderboard",description="")
        all_docs = list(collection.find().sort("coal", pymongo.DESCENDING).limit(10))
        all_docs2 = list(collection.find().sort("coal", pymongo.DESCENDING))
        for i in all_docs:
            text = text + f"{all_docs.index(i)+1}    |    {i['name']}: {i['coal']}\n"
        embed.add_field(name="Global Coal Ranking", value=text, inline=True)
        list_id_in_server = ctx.guild.members
        text = ""
        count = 0
        for userid in list_id_in_server:
            idlist.append(userid.id)
        for i in all_docs2:
            if i['user_id'] in idlist:
                count += 1
                text = text + f"{count}    |    {i['name']}: {i['coal']}\n"
            if count == 10:            
                break
        embed.add_field(name="Server Coal Ranking:", value=text, inline=True)
        await ctx.send(embed=embed)


    

    @commands.hybrid_command(name="profile", aliases=["pf"], description="Show user's profile")
    async def profile(self, ctx, user: discord.Member = None):
        if user == None:
            userid = ctx.author.id
            userinfo = collection.find_one({"user_id": ctx.author.id})
        elif user != None:
            userid = user.id
            userinfo = collection.find_one({"user_id": user.id})
        if userinfo == None:
            embed = discord.Embed(description="*This user is bot/was not registered*")
            await ctx.defer(ephemeral=False)
            await ctx.reply(embed=embed)
        elif userinfo != None:
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
            listexpperlvl = userinfo["expmaxperlv"]
            start = 0
            end = 0.1
            if userinfo["Lv"] > 1:
                percentage = (userinfo["exp"]-listexpperlvl[userinfo["Lv"]-2])/(listexpperlvl[userinfo["Lv"]-1]-listexpperlvl[userinfo["Lv"]-2])
                for bar in range(len(progressbar)):
                    if percentage >= start and percentage < end:
                        result = progressbar[bar]
                        break
                    else:
                        start += 0.1
                        end += 0.1
            elif userinfo["Lv"] == 1:
                for bar in range(len(progressbar)):
                    if userinfo["exp"]/listexpperlvl[0] >= start and userinfo["exp"]/listexpperlvl[0] < end:
                        result = progressbar[bar]
                        break
                    else:
                        start += 0.1
                        end += 0.1
            all_docs = list(collection.find().sort("coal", pymongo.DESCENDING))
            topcount = 1
            for i in all_docs:
                if i["user_id"] == userid:
                    break
                else:
                    topcount += 1
            
            embed = discord.Embed(title=f"{userinfo['name']}'s profile", 
                                description=f"<:charcoal:1400474440579682508> | ***Coal:*** 「{int(userinfo['coal'])}」\n<:charcoalwtrophy:1402578408730529814> | ***Global Coal Ranking:*** 「#{topcount}」\n<:exp:1402574443955622039> | ***Level {userinfo['Lv']}***ㅤ***/***{result}***/***「{userinfo['exp']}/{listexpperlvl[userinfo['Lv']-1]}」")
            if user == None:
                embed.set_thumbnail(url=ctx.author.avatar)
            else:
                embed.set_thumbnail(url=user.avatar)
            await ctx.defer(ephemeral=False)
            await ctx.reply(embed=embed)

    @commands.command(name="sync")
    async def sync(self, ctx):
        try:
            await self.bot.tree.sync(guild=(discord.Object(id=1274638308533600286)))
            await ctx.send("Sync completed!")
        except Exception:
            await ctx.send("Sync failed!")
            traceback.print_exc()
        except discord.app_commands.CommandSyncFailure:
            await ctx.send("Sync failed!")
            traceback.print_exc()
            


            
async def setup(bot):
    await bot.add_cog(RPG(bot))