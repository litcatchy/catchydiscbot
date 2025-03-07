import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        """Handles errors globally for this cog and sends error messages to Discord."""
        embed = discord.Embed(color=discord.Color.red())
        embed.description = f"<:cancel:1346853536738316339> "

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description += f"Missing required argument: `{error.param.name}`"
        elif isinstance(error, commands.BadArgument):
            embed.description += "Invalid argument provided."
        elif isinstance(error, commands.MissingPermissions):
            embed.description += "You don’t have permission to use this command."
        elif isinstance(error, commands.CommandInvokeError):
            embed.description += f"An error occurred: `{error.original}`"
        else:
            embed.description += f"Unexpected error: `{error}`"

        await ctx.send(embed=embed)

    async def send_embed(self, ctx, description, color=discord.Color.green()):
        """Helper function to send an embed message."""
        embed = discord.Embed(description=description, color=color)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=embed)

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner", discord.Color.red())

        await member.kick(reason=reason)
        await self.send_embed(ctx, f"<:success:1346853488738566175> Successfully kicked {member.mention}.\n**Reason:** {reason}")

    # Ban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner", discord.Color.red())

        await member.ban(reason=reason)
        await self.send_embed(ctx, f"<:success:1346853488738566175> Successfully banned {member.mention}.\n**Reason:** {reason}")

    # Unban Command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        banned_users = await ctx.guild.bans()
        user = discord.utils.get(banned_users, user=lambda u: u.user.id == user_id)

        if user is None:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> That user is not banned.", discord.Color.red())

        await ctx.guild.unban(user.user)
        await self.send_embed(ctx, f"<:success:1346853488738566175> Successfully unbanned {user.user.mention}.")

    # Timeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner", discord.Color.red())

        time_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_multipliers or not duration[:-1].isdigit():
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Invalid time format! Use `10m`, `1h`, `1d`, etc.", discord.Color.red())

        seconds = int(duration[:-1]) * time_multipliers[unit]
        duration_time = timedelta(seconds=seconds)

        await member.timeout(discord.utils.utcnow() + duration_time, reason=reason)
        await self.send_embed(ctx, f"<:success:1346853488738566175> Successfully timed out {member.mention} for {duration}.\n**Reason:** {reason}")

    # Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        if member.timed_out_until is None:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> That user is not currently timed out.", discord.Color.red())

        await member.timeout(None)
        await self.send_embed(ctx, f"<:success:1346853488738566175> Successfully removed timeout for {member.mention}.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
