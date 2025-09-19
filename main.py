import discord
from discord.ext import commands
import os
import asyncio
import traceback
from format import num_unformat, num_format
from secret import discordtoken

class MyBot(commands.AutoShardedBot):
    async def setup_hook(self):
        cogs_directory = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_directory):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename[:-3]}")

bot = MyBot(command_prefix="c!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        await bot.change_presence(status=discord.Status.invisible)
        count = 0
        for guild in bot.guilds:
            count += 1
            bot.tree.clear_commands(guild=discord.Object(id=guild.id))
            bot.tree.copy_global_to(guild=discord.Object(id=guild.id))        
            await bot.tree.sync(guild=discord.Object(id=guild.id))
            print(f"Syncing all slash commands for {count}/{len(bot.guilds)}...", end="\r")
            if count == len(bot.guilds):
                print(f"\rCompleted syncing all slash commands for {count}/{len(bot.guilds)} servers")
                break
            await asyncio.sleep(20)
        await bot.change_presence(activity=discord.Streaming(name=f"a game on {num_format(len(bot.guilds))} servers", url="https://www.twitch.tv/charcoalakahaze"), status=discord.Status.online)
        print("Bot ready!")
    except Exception:
        traceback.print_exc()

@bot.event
async def on_guild_join(guild):
    bot.tree.clear_commands(guild=discord.Object(id=guild.id))
    bot.tree.copy_global_to(guild=discord.Object(id=guild.id))
    await bot.tree.sync(guild=discord.Object(id=guild.id))
    await bot.change_presence(activity=discord.Streaming(name=f"on {len(bot.guilds)}", url=""), status=discord.Status.online)

@bot.event
async def on_guild_remove(guild):
    bot.tree.clear_commands(guild=discord.Object(id=guild.id))
    await bot.tree.sync(guild=discord.Object(id=guild.id))
    await bot.change_presence(activity=discord.Streaming(name=f"on {len(bot.guilds)}", url=""), status=discord.Status.online)

async def main():
    async with bot:
        await bot.start(discordtoken)

if __name__ == "__main__":
    asyncio.run(main())