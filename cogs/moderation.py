import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kicks a user from the server."""

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to kick.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> I don’t have permission to kick members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been kicked.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Bans a user from the server."""

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to ban.",
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

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot ban {member.mention} because they have a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I do not have permission to ban members.",
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

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: int = None, *, reason: str = "No reason provided"):
        """Times out a user for a certain duration (in minutes)."""

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if duration is None or duration <= 0:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You must provide a valid duration in minutes.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout_for(duration * 60, reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been timed out for {duration} minutes.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes timeout from a user."""

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to remove timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout_for(None)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} timeout has been removed.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Untimed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
