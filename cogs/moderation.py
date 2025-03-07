from discord.ext import commands
import discord
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Add the skill issue message for the bot owner
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return False
        return True

    @commands.command()
    async def timeout(self, ctx, member: discord.Member, time: str):
        """Timeout a member for a specified time (e.g. 10m, 1h, 1d)."""
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return

        time_units = {'m': 'minutes', 'h': 'hours', 'd': 'days'}

        try:
            unit = time[-1]
            value = int(time[:-1])
            if unit not in time_units:
                await ctx.send("Invalid time unit. Use 'm' for minutes, 'h' for hours, 'd' for days.")
                return
        except ValueError:
            await ctx.send("Invalid time format. Example: `10m`, `1h`, `1d`.")
            return

        timeout_duration = timedelta(**{time_units[unit]: value})

        try:
            await member.timeout(timeout_duration)
            await ctx.send(f"{member.mention} has been successfully timed out for {time} <:success:1346853488738566175>.")
        except discord.Forbidden:
            await ctx.send(f"I don't have permission to timeout {member.mention} <:cancel:1346853536738316339>.")
        except discord.HTTPException:
            await ctx.send(f"An error occurred while trying to timeout {member.mention} <:cancel:1346853536738316339>.")

    @commands.command()
    async def untimeout(self, ctx, member: discord.Member):
        """Remove timeout from a member."""
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return

        if member.communication_disabled_until is None:
            await ctx.send(f"{member.mention} is not timed out. <:cancel:1346853536738316339>")
        else:
            try:
                await member.timeout(None)
                await ctx.send(f"{member.mention} has been successfully untimed out. <:success:1346853488738566175>")
            except discord.Forbidden:
                await ctx.send(f"I don't have permission to untimeout {member.mention} <:cancel:1346853536738316339>.")
            except discord.HTTPException:
                await ctx.send(f"An error occurred while removing the timeout for {member.mention} <:cancel:1346853536738316339>.")

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server."""
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return

        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned. <:success:1346853488738566175>")
        except discord.Forbidden:
            await ctx.send(f"I don't have permission to ban {member.mention} <:cancel:1346853536738316339>.")
        except discord.HTTPException:
            await ctx.send(f"An error occurred while banning {member.mention} <:cancel:1346853536738316339>.")

    @commands.command()
    async def unban(self, ctx, user: discord.User):
        """Unban a member from the server."""
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return

        banned_users = await ctx.guild.bans()
        banned_user = discord.utils.get(banned_users, user=user)
        if banned_user:
            try:
                await ctx.guild.unban(user)
                await ctx.send(f"{user.mention} has been unbanned. <:success:1346853488738566175>")
            except discord.Forbidden:
                await ctx.send(f"I don't have permission to unban {user.mention} <:cancel:1346853536738316339>.")
            except discord.HTTPException:
                await ctx.send(f"An error occurred while unbanning {user.mention} <:cancel:1346853536738316339>.")
        else:
            await ctx.send(f"{user.mention} is not banned. <:cancel:1346853536738316339>")

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server."""
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return

        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked. <:success:1346853488738566175>")
        except discord.Forbidden:
            await ctx.send(f"I don't have permission to kick {member.mention} <:cancel:1346853536738316339>.")
        except discord.HTTPException:
            await ctx.send(f"An error occurred while kicking {member.mention} <:cancel:1346853536738316339>.")

    @commands.command()
    async def reload(self, ctx, extension):
        """Reload a cog. Only available to the server owner."""
        if ctx.author.id != self.bot.owner_id:
            await ctx.send(f"<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")
            return

        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            await ctx.send(f"{extension} has been reloaded. <:success:1346853488738566175>")
        except Exception as e:
            await ctx.send(f"Error reloading {extension}: {str(e)} <:cancel:1346853536738316339>")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
