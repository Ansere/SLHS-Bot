from discord import Embed
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from member_commands import ServerMembers
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from servermembers import *
from db import bind_engine


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('s.'), intents=intents)
bot.remove_command('help')
engine = create_engine("sqlite+pysqlite:///sqlite3", echo=True, future=True, connect_args={"check_same_thread": False})


@bot.event
async def on_ready():
    bind_engine(engine)
    load_members(bot)

@bot.command(aliases = ['h'])
async def help(ctx):
    embedVar = Embed(title = "SLHS Bot")
    embedVar.add_field(name = "Commands", value = "\n".join([str(command) for command in bot.commands]))
    await ctx.send(embed = embedVar)

bot.add_cog(ServerMembers(bot))
bot.run(TOKEN)

