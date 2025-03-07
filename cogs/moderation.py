import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: int = None, *, reason: str = "No reason provided"):
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> You must mention a user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I do not have permission to timeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(duration, reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been timed out by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def untimeout(self, ctx, member: discord.Member = None):
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> You must mention a user to remove timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} timeout removed by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if not ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Kick Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> You must mention a user to kick.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been kicked by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.guild.owner:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot ban {member.mention} because they have a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await ctx.guild.ban(member, reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} got banned by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I do not have permission to ban {member.mention}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> The user {member.mention} does not exist or is already banned.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
