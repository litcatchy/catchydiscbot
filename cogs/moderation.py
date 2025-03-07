import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        """Handles errors globally for this cog and sends error messages to Discord."""
        embed = discord.Embed(color=discord.Color.red())

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"<:cancel:1346853536738316339> Missing required argument: `{error.param.name}`"
        elif isinstance(error, commands.BadArgument):
            embed.description = "<:cancel:1346853536738316339> Invalid argument provided."
        elif isinstance(error, commands.MissingPermissions):
            embed.description = "<:cancel:1346853536738316339> You don’t have permission to use this command."
        elif isinstance(error, commands.CommandInvokeError):
            embed.description = f"<:cancel:1346853536738316339> An error occurred: `{error.original}`"
        else:
            embed.description = f"<:cancel:1346853536738316339> Unexpected error: `{error}`"

        await ctx.send(embed=embed)

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            embed = discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner", color=discord.Color.red())
            return await ctx.send(embed=embed)

        await member.kick(reason=reason)
        embed = discord.Embed(description=f"<:success:1346853488738566175> Successfully kicked {member.mention}. Reason: {reason}", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Ban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            embed = discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner", color=discord.Color.red())
            return await ctx.send(embed=embed)

        await member.ban(reason=reason)
        embed = discord.Embed(description=f"<:success:1346853488738566175> Successfully banned {member.mention}. Reason: {reason}", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Unban Command (Fixed)
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        banned_users = [entry async for entry in ctx.guild.bans()]  # Correct async iteration
        user = next((entry.user for entry in banned_users if entry.user.id == user_id), None)

        if user is None:
            embed = discord.Embed(description="<:cancel:1346853536738316339> That user is not banned.", color=discord.Color.red())
            return await ctx.send(embed=embed)

        await ctx.guild.unban(user)
        embed = discord.Embed(description=f"<:success:1346853488738566175> Successfully unbanned {user.mention}.", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Timeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            embed = discord.Embed(description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner", color=discord.Color.red())
            return await ctx.send(embed=embed)

        time_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_multipliers or not duration[:-1].isdigit():
            embed = discord.Embed(description="<:cancel:1346853536738316339> Invalid time format! Use `10m`, `1h`, `1d`, etc.", color=discord.Color.red())
            return await ctx.send(embed=embed)

        seconds = int(duration[:-1]) * time_multipliers[unit]
        duration_time = timedelta(seconds=seconds)

        await member.timeout(discord.utils.utcnow() + duration_time, reason=reason)
        embed = discord.Embed(description=f"<:success:1346853488738566175> Successfully timed out {member.mention} for {duration}. Reason: {reason}", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        if member.timed_out_until is None:
            embed = discord.Embed(description="<:cancel:1346853536738316339> That user is not currently timed out.", color=discord.Color.red())
            return await ctx.send(embed=embed)

        await member.timeout(None)
        embed = discord.Embed(description=f"<:success:1346853488738566175> Successfully removed timeout for {member.mention}.", color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
