import discord
from discord.ext import commands
import datetime
import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔨 Kick Command (Handles invalid users)
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: str = None, *, reason: str = "No reason provided"):
        """Kicks a user from the server."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a valid user to kick.", color=discord.Color.red()))

        member_obj = discord.utils.get(ctx.guild.members, mention=member) or discord.utils.get(ctx.guild.members, id=int(member) if member.isdigit() else None)

        if not member_obj:
            return await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> The user `{member}` is not in the server.", color=discord.Color.red()))

        if ctx.guild.owner_id == member_obj.id:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Skill issue, you can't use this command on the server owner.", color=discord.Color.red()))

        if ctx.author.top_role <= member_obj.top_role:
            return await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> You cannot kick {member_obj.mention} because they have a higher or equal role.", color=discord.Color.red()))

        try:
            await member_obj.kick(reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member_obj.mention} has been kicked.\n**Reason:** {reason}", color=discord.Color.green()))
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> I do not have permission to kick {member_obj.mention}.", color=discord.Color.red()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`", color=discord.Color.red()))

    # 🔨 Ban Command (Handles invalid users)
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: str = None, *, reason: str = "No reason provided"):
        """Bans a user from the server using mention or ID."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a valid user to ban.", color=discord.Color.red()))

        try:
            user = await self.bot.fetch_user(int(member) if member.isdigit() else member.strip("<@!>"))
        except discord.NotFound:
            return await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> The user `{member}` does not exist.", color=discord.Color.red()))
        except ValueError:
            return await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Invalid user ID or mention.", color=discord.Color.red()))

        try:
            await ctx.guild.ban(user, reason=reason)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {user.mention} has been banned.\n**Reason:** {reason}", color=discord.Color.green()))
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> I do not have permission to ban {user.mention}.", color=discord.Color.red()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to ban.\nError: `{e}`", color=discord.Color.red()))

    # 🔨 Unban Command (Supports User ID)
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str):
        """Unbans a user using mention or ID."""
        try:
            user_obj = await self.bot.fetch_user(int(user) if user.isdigit() else user.strip("<@!>"))
            await ctx.guild.unban(user_obj)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {user_obj.mention} has been unbanned.", color=discord.Color.green()))
        except discord.NotFound:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> The user `{user}` is not banned or does not exist.", color=discord.Color.red()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to unban.\nError: `{e}`", color=discord.Color.red()))

    # 🔨 Timeout Command (Supports `10m`, `1d`, etc.)
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        """Timeouts a user for a specified duration."""
        if not member:
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a valid user to timeout.", color=discord.Color.red()))

        if not duration:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> You must specify a duration.\nExample: `10m` (10 minutes), `1h` (1 hour), `1d` (1 day).", color=discord.Color.red()))

        unit_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        match = re.match(r"(\d+)([smhd])", duration.lower())

        if not match:
            return await ctx.send(embed=discord.Embed(description="<:cancel:1346853536738316339> Invalid duration format. Use `s`, `m`, `h`, or `d`.\nExample: `10m`, `1h`, `1d`", color=discord.Color.red()))

        amount, unit = match.groups()
        timeout_seconds = int(amount) * unit_multipliers[unit]
        timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=timeout_seconds)

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
            return await ctx.send(embed=discord.Embed(description="<:mention:1347449690849022092> You must mention a valid user to untimeout.", color=discord.Color.red()))

        try:
            await member.edit(timed_out_until=None)
            await ctx.send(embed=discord.Embed(description=f"<:success:1346853488738566175> {member.mention} has been un-timed out.", color=discord.Color.green()))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`", color=discord.Color.red()))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
