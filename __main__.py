from dotenv import load_dotenv
from discord.ext import commands
from discord import Embed
import calendarcore
import discord
import asyncio
import sqlite3
import os
import embed

#initialization of bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('s.'), intents=intents)
bot.remove_command('help')

#sql
DIR = os.path.dirname(__file__)
db = sqlite3.connect(os.path.join(DIR, "Users.db"))
SQL = db.cursor()
SQL.execute("CREATE TABLE IF NOT EXISTS users (number INTEGER PRIMARY KEY, id INTEGER NOT NULL, description text NOT NULL DEFAULT 'A SLHS Student.', name text)")
SQL.execute("SELECT id from users")
a = SQL.fetchall()

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id == 748995290006028399:
            break
    for member in [member.id for member in guild.members if member.bot == False]:
        if not(member in [item[0] for item in a]):
            SQL.execute("INSERT INTO users (id) VALUES(?)", (member,))
            db.commit()
            renumber()
    for num, member in enumerate([guild.get_member(member[0]) for member in a]):
        try:
            member.mention
        except:
            print(f"Member with rowid {num + 1} has an invalid id!")
            SQL.execute("DELETE from users where rowid = ?", (num+1,))
            db.commit()
            renumber()
    renumber()
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(pass_context = True, aliases = ["rn"])
async def realname(ctx):
    name = getName(ctx)
    embedVar = Embed(title = "Doxxed...", description = name)
    await ctx.send(embed = embedVar)

@bot.command(aliases = ['u'])
async def update(ctx, *args):
    args = list(args)
    member = ctx.message.author

    try:
        message = update(args.pop(0), " ".join(args), member)
        embedVar = Embed(title = "Updated successfully", description = message)
    except:
        embedVar = Embed(title = "Task failed", description = ":(")
    await ctx.send(embed = embedVar)

@bot.command(aliases = ['h'])
async def help(ctx):
    embedVar = Embed(title = "SLHS Bot")
    embedVar.add_field(name = "Commands", value = "\n".join([str(command) for command in bot.commands]))
    await ctx.send(embed = embedVar)

@bot.command(aliases = ['su'])
async def sqlu(ctx, *args):
    try:
        member = ctx.message.mentions[0]
        args = args.remove(member.mention)
    except:
        member = ctx.message.author
    if await bot.is_owner(ctx.message.author):
        try:
            SQL.execute(f"UPDATE {args[0]} SET {args[1]} = ? WHERE {args[2]} = ?", (args[4], member.id))
        except(Exception):
            await ctx.send(Exception)
    else:
        await ctx.send(error.InsufficientPermissionsException("Bot Owner"))


@bot.command(aliases = ['p'])
async def profile(ctx):
    member = ctx.message.author
    if len(ctx.message.mentions) > 0:
        member = ctx.message.mentions[0]
    SQL.execute(f"SELECT description, rowid from users WHERE id = {member.id} and description is not null")
    info = SQL.fetchone()
    description = info[0]
    embedVar = Embed(title = f"{member.name}'s profile", description = description, color = [role for role in member.roles if role.hoist][-1].color)
    embedVar.set_thumbnail(url = str(member.avatar_url))
    embedVar.set_footer(text = f"Member #{info[1]}", icon_url = str(ctx.message.guild.icon_url))
    await ctx.send(embed = embedVar)

@bot.command(aliases = ['m'])
async def members(ctx):
    message = await ctx.send(embed = createMemberList(ctx, 1))
    for emoji in ('◀', '▶'):
        await message.add_reaction(emoji)
    index = 1;
    def check(reaction,user):
        return checkBot(user) and str(reaction.emoji) in ['▶', '◀'] and reaction.message.id == message.id
    def checkBot(user):
        return user.bot == False
    while True:
        try:
            reaction = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            break
        if reaction[0].emoji == "◀":
            user = await reaction[0].users().find(checkBot)
            await reaction[0].remove(user=user)
            if index <= 1:
                continue
            else:
                index -= 1
                await message.edit(embed = createMemberList(ctx, index))
        else:
            user = await reaction[0].users().find(checkBot)
            await reaction[0].remove(user = user)
            SQL.execute("SELECT rowid from users")
            members = len(SQL.fetchall())
            if index >= ((members//10) + 1):
                print(index)
                continue
            else:
                index += 1
                await message.edit(embed=createMemberList(ctx, index))

@bot.command(aliases = ['c'])
async def calendar(ctx):
    try:
        bot.add_cog(calendarcore.Calendar(bot))
        await ctx.send("Added Calendar cog!")
    except:
        bot.remove_cog("Calendar")
        await ctx.send("Removed Calendar cog!")

@bot.event
async def on_member_join(member):
    if not(member in [item[0] for item in a]):
        SQL.execute("INSERT INTO users (id) VALUES(?)", (member.id,))
        db.commit()
    renumber()

@bot.event
async def on_member_remove(member):
    SQL.execute("DELETE from users where id = ?", (member.id,))
    db.commit()
    renumber()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        command = str(error).split("\"")[1];
        if (command in ["addclass"]):
            await ctx.send(embed=embed.ErrorEmbed(errormsg="Command in Calendar Cog not enabled: do `s.calendar` to enable.").getembed())

def errorEmbed(message):
    return Embed(title = "Task failed", description = message)

def getName(ctx):
    SQL.execute("SELECT id from users")
    member = ctx.message.author
    if len(ctx.message.mentions) > 0:
        member = ctx.message.mentions[0]
    ids = [a[0] for a in SQL.fetchall()]
    if member.id in ids:
        try:
            SQL.execute(f"SELECT name from users WHERE id = {member.id} and name is not null")
            return member.mention + "'s real name is " + SQL.fetchone()[0]
        except:
            return member.mention + " has not set their real name"
    else:
        return "Hm, you aren't in the database"

def update(column, data, member):
    try:
        if column.lower() in ['number', 'id']:
            return "Forbidden edit!"
        SQL.execute(f"UPDATE users SET {column} = ? where id = ?", (data, member.id))
        db.commit()
        return f"{column} set to {data}"
    except:
        return 0

def createMemberList(ctx, page):
    SQL.execute("SELECT rowid, id from users")
    info = SQL.fetchall()
    list = ""
    for i in range(10):
        try:
            member = info[i + (page - 1) * 10]
            print(member)
            list += f"{member[0]}. {ctx.message.guild.get_member(member[1]).mention}\n"
        except:
            break
    print(list)
    embedVar = Embed(title="SLHS Bot", description = "Members")
    embedVar.add_field(name="hm", value=list)
    return embedVar

def renumber():
    SQL.execute("SELECT id from users")
    for num, id in enumerate(SQL.fetchall()):
        SQL.execute("UPDATE users SET number = ? where id = ?", (num + 1, id[0]))
        db.commit()


bot.run(TOKEN)
