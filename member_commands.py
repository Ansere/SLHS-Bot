from discord.ext import commands
from discord import Embed
from servermembers import get_server_member, ServerMember, session
import customembed
listclasses = []
list_servermembers = session.query(ServerMember)

class ServerMembers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['u'])
    async def update(self, ctx, *args):
        editable_columns = ["real_name", "description"]
        if len(args) < 1:
            await customembed.ErrorEmbed(errormsg=f"Insufficient arguments! \nUsage: `s.update [{'|'.join(editable_columns)}] [data]`").send(ctx=ctx)
            return
        args = list(args)
        user = ctx.message.author
        if ctx.message.author.guild_permissions.administrator and len(ctx.message.mentions) > 0:
            user = ctx.message.mentions[0]
        member = get_server_member(user.id)
        try:
            column = args.pop(0).lower()
            data = " ".join(args)
            if column in editable_columns:
                getattr(ServerMember, "set_" + column)(member, data)
                await ctx.send(embed=Embed(title="Updated successfully", description=f"Updated {user.mention}'s {column} to {data}"))
            else:
                await customembed.ErrorEmbed(errormsg="Invalid column name").send(ctx = ctx)
        except(Exception):
            await customembed.ErrorEmbed(errormsg="An exception occured. Please log this in a ticket.").send(ctx = ctx)
            raise Exception

    @commands.command(pass_context=True, aliases=["rn"])
    async def realname(self, ctx):
        member = ctx.message.author
        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
        name = get_server_member(member.id).real_name

        if isinstance(name, str) and len(name) > 0:
            await ctx.send(embed=Embed(title="Doxxed...", description=f"{member.mention}'s real name is {name}"))
        else:
            await ctx.send(embed=Embed(title="?", description=f"{member.mention} has not set their real name"))

    @commands.command(aliases=['p'])
    async def profile(self, ctx):
        member = ctx.message.author
        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
        servermember = get_server_member(member.id)
        embedVar = Embed(title=f"{member.name}'s profile", description=servermember.description,
                         color=member.top_role.color)
        embedVar.set_thumbnail(url=str(member.avatar_url))
        embedVar.set_footer(text=f"Member #{servermember.id}",
                            icon_url=str(ctx.message.guild.icon_url))
        await ctx.send(embed=embedVar)

    @commands.command(aliases=['m'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def members(self, ctx):
        await customembed.NavigatableEmbed(
            pages=[createMemberList(ctx, i + 1) for i in range(list_servermembers.count() // 10 + 1)], title="SLHS Class of 2024",
            color=0xffab57).send(ctx)

def createMemberList(ctx, page):
    list = ""
    for i in range(10):
        try:
            member = list_servermembers.all()[i + (page - 1) * 10]
            print("hi")
            print(member)
            list += f"{i + (page - 1) * 10 + 1}. {ctx.message.guild.get_member(member.discord_id).mention}\n"
            print("there")
        except:
            break
    embedVar = Embed(title="SLHS Bot", description=f"{list_servermembers.count()} members")
    embedVar.add_field(name="hm", value=list)
    return embedVar