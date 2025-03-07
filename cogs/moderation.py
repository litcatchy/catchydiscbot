import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        """Handles errors globally for this cog and sends error messages to Discord."""
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name="Error", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

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

    async def send_embed(self, ctx, title, description, color=discord.Color.green()):
        """Helper function to send an embed message."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=embed)

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, "Skill Issue", "Slaves cannot use the command on the server owner.", discord.Color.red())

        await member.kick(reason=reason)
        await self.send_embed(ctx, "Kick Successful", f"{member.mention} has been kicked.\n**Reason:** {reason}")

    # Ban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, "Skill Issue", "Slaves cannot use the command on the server owner.", discord.Color.red())

        await member.ban(reason=reason)
        await self.send_embed(ctx, "Ban Successful", f"{member.mention} has been banned.\n**Reason:** {reason}")

    # Unban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        banned_users = await ctx.guild.bans()
        user = discord.utils.get(banned_users, user=lambda u: u.user.id == user_id)

        if user is None:
            return await self.send_embed(ctx, "Error", "That user is not banned.", discord.Color.red())

        await ctx.guild.unban(user.user)
        await self.send_embed(ctx, "Unban Successful", f"{user.user.mention} has been unbanned.")

    # Timeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, "Skill Issue", "Slaves cannot use the command on the server owner.", discord.Color.red())

        time_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_multipliers or not duration[:-1].isdigit():
            return await self.send_embed(ctx, "Error", "Invalid time format! Use `10m`, `1h`, `1d`, etc.", discord.Color.red())

        seconds = int(duration[:-1]) * time_multipliers[unit]
        duration_time = timedelta(seconds=seconds)

        await member.timeout(discord.utils.utcnow() + duration_time, reason=reason)
        await self.send_embed(ctx, "Timeout Successful", f"{member.mention} has been timed out for **{duration}**.\n**Reason:** {reason}")

    # Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        if member.timed_out_until is None:
            return await self.send_embed(ctx, "Error", "That user is not currently timed out.", discord.Color.red())

        await member.timeout(None)
        await self.send_embed(ctx, "Untimeout Successful", f"{member.mention}'s timeout has been removed.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
