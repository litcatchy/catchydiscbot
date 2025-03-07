import discord
from discord.ext import commands
import datetime
import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Timeout Command
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

        unit_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        match = re.match(r"(\d+)([smhd])", duration.lower())

        if not match:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Invalid duration. Use `s` for seconds, `m` for minutes, `h` for hours, `d` for days.", color=discord.Color.red()))

        amount, unit = match.groups()
        timeout_seconds = int(amount) * unit_multipliers[unit]
        timeout_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=timeout_seconds)

        try:
            await member.edit(timed_out_until=timeout_until, reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been timed out for `{duration}`.\n**Reason:** {reason}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to timeout.\nError: `{e}`", color=discord.Color.red()))

    # Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes timeout from a user."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user to untimeout.", color=discord.Color.red()))

        try:
            await member.edit(timed_out_until=None)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been untimed out.", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`", color=discord.Color.red()))

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kicks a user from the server."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user to kick.", color=discord.Color.red()))

        if member == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.", color=discord.Color.red()))

        try:
            await member.kick(reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been kicked.\n**Reason:** {reason}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`", color=discord.Color.red()))

    # Ban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Bans a user from the server."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user to ban.", color=discord.Color.red()))

        if member == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.", color=discord.Color.red()))

        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been banned.\n**Reason:** {reason}", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to ban.\nError: `{e}`", color=discord.Color.red()))

    # Unban Command (Supports User ID)
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str = None):
        """Unbans a user from the server by mention or user ID."""
        if not user:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a user or provide a User ID to unban.", color=discord.Color.red()))

        try:
            user_id = int(user) if user.isdigit() else None
            bans = await ctx.guild.bans()
            banned_user = None

            if user_id:
                banned_user = next((ban_entry.user for ban_entry in bans if ban_entry.user.id == user_id), None)
            else:
                banned_user = next((ban_entry.user for ban_entry in bans if ban_entry.user.mention == user), None)

            if not banned_user:
                return await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> No banned user found with ID `{user}`.", color=discord.Color.red()))

            await ctx.guild.unban(banned_user)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {banned_user.mention} has been unbanned.", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to unban.\nError: `{e}`", color=discord.Color.red()))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
