import discord
from discord.ext import commands
import datetime
import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔨 Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kicks a user from the server."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user to kick.", color=discord.Color.red()))

        if member == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.", color=discord.Color.red()))

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> You cannot kick someone with a higher or equal role.", color=discord.Color.red()))

        try:
            await member.kick(reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been kicked.\n**Reason:** {reason}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`", color=discord.Color.red()))

    # 🔨 Ban Command
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Bans a user from the server."""
        if member == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.", color=discord.Color.red()))

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> You cannot ban {member.mention} because they have a higher or equal role.", color=discord.Color.red()))

        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been banned.\n**Reason:** {reason}", color=discord.Color.green()))
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> I do not have permission to ban {member.mention}.", color=discord.Color.red()))
        except discord.NotFound:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> The user {member.mention} does not exist or is already banned.", color=discord.Color.red()))

    # 🔨 Unban Command (Mention or User ID)
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User):
        """Unbans a user from the server using mention or user ID."""
        try:
            await ctx.guild.unban(user)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {user.mention} has been unbanned.", color=discord.Color.green()))
        except discord.NotFound:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> The user {user.mention} is not banned or does not exist.", color=discord.Color.red()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to unban.\nError: `{e}`", color=discord.Color.red()))

    # 🔨 Timeout Command (Fixed Duration Parsing)
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        """Timeouts a user for a specific duration."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user to timeout.", color=discord.Color.red()))

        if not duration:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> You must specify a duration.\nExample: `10m` for 10 minutes, `1h` for 1 hour, `1d` for 1 day.", color=discord.Color.red()))

        if member == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.", color=discord.Color.red()))

        # Convert duration to seconds
        unit_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        match = re.match(r"(\d+)([smhd])", duration.lower())

        if not match:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Invalid duration. Use `s` (seconds), `m` (minutes), `h` (hours), `d` (days).\nExample: `10m`, `1h`, `2d`", color=discord.Color.red()))

        amount, unit = match.groups()
        timeout_seconds = int(amount) * unit_multipliers[unit]
        timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=timeout_seconds)  # FIXED

        try:
            await member.edit(timed_out_until=timeout_until, reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been timed out for `{duration}`.\n**Reason:** {reason}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to timeout.\nError: `{e}`", color=discord.Color.red()))

    # 🔨 Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes a timeout from a user."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user to untimeout.", color=discord.Color.red()))

        try:
            await member.edit(timed_out_until=None)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been un-timed out.", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`", color=discord.Color.red()))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
