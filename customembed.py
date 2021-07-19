from discord.colour import Color
from discord import Embed
from typing import List
import discord
import asyncio

class ErrorEmbed():
    def __init__ (self, errormsg = "", title = "Something went wrong...", color = Color.red()):
        self.errormsg = errormsg
        self.title = title
        self.color = color

    def getembed(self):
        return Embed(color=self.color, title=self.title, description= self.errormsg)

    async def send(self, ctx, delay = 5.0):
        error = await ctx.send(embed=self.getembed())
        await error.delete(delay=delay)

class NavigatableEmbed():
    def __init__ (self, pages : List[Embed], files = None, title = None, color = None):
        self.pages = pages
        self.files = files
        print(files)
        if title is not None:
            for page in pages:
                page.title = title
        if color is not None:
            for page in pages:
                page.color = color

    async def send(self, ctx):
        if self.files is not None:
            message = await ctx.send(file=discord.File(self.files[0], filename="media.png"), embed=self.pages[0])
        else:
            message = await ctx.send(embed = self.pages[0])
        for emoji in ('◀', '▶'):
            await message.add_reaction(emoji)
        index = 0;
        def check(reaction, user):
            return checkBot(user) and str(reaction.emoji) in ['▶', '◀'] and reaction.message.id == message.id
        def checkBot(user):
            return user.bot == False
        while True:
            try:
                reaction = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                break
            if reaction[0].emoji == "◀":
                user = await reaction[0].users().find(checkBot)
                await reaction[0].remove(user=user)
                if index <= 0:
                    index = len(self.pages) - 1
                else:
                    index -= 1
            elif reaction[0].emoji == "▶":
                user = await reaction[0].users().find(checkBot)
                await reaction[0].remove(user=user)
                if index >= len(self.pages) - 1:
                    index = 0
                else:
                    index += 1
            else:
                break
            if self.files is not None:
                await message.delete()
                message = await ctx.send(file =discord.File(self.files[index], filename="media.png"), embed = self.pages[index])
                for emoji in ('◀', '▶'):
                    await message.add_reaction(emoji)
            else:
                await message.edit(embed=self.pages[index])
