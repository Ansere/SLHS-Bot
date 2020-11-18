import sqlite3
from discord.ext import commands

class Calendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot;

    @commands.command(aliases=['ac'])
    async def addclass(self, ctx, *args):
        await ctx.send("hi!");