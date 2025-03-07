import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await ctx.send("<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
        await member.kick(reason=reason)
        await ctx.send(f"<:success:1346853488738566175> Successfully kicked {member.mention}. Reason: {reason}")

    # Ban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await ctx.send("<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
        await member.ban(reason=reason)
        await ctx.send(f"<:success:1346853488738566175> Successfully banned {member.mention}. Reason: {reason}")

    # Unban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        banned_users = await ctx.guild.bans()
        user = discord.utils.get(banned_users, user=lambda u: u.user.id == user_id)

        if user is None:
            return await ctx.send("<:cancel:1346853536738316339> That user is not banned.")

        await ctx.guild.unban(user.user)
        await ctx.send(f"<:success:1346853488738566175> Successfully unbanned {user.user.mention}.")

    # Timeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await ctx.send("<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")

        time_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_multipliers or not duration[:-1].isdigit():
            return await ctx.send("<:cancel:1346853536738316339> Invalid time format! Use `10m`, `1h`, `1d`, etc.")

        seconds = int(duration[:-1]) * time_multipliers[unit]

        await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds), reason=reason)
        await ctx.send(f"<:success:1346853488738566175> Successfully timed out {member.mention} for {duration}. Reason: {reason}")

    # Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        if member.timed_out_until is None:
            return await ctx.send("<:cancel:1346853536738316339> That user is not currently timed out.")

        await member.timeout(None)
        await ctx.send(f"<:success:1346853488738566175> Successfully removed timeout for {member.mention}.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
