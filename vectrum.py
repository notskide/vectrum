import os
import sys
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="v!", intents=intents)

@bot.event
async def on_ready():
    print(f'Vectrum Engine Online: Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

async def load_extensions():
    await bot.load_extension("cogs.prediction")

async def main():
    keep_alive()
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
