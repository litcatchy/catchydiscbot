import discord
from discord.ext import commands
import re
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def convert_time(self, time_str):
        """Converts a time string (e.g., '10m', '2h') into a timedelta object."""
        match = re.match(r"^(\d+)([smhd])$", time_str)
        if not match:
            return None
        
        num, unit = int(match.group(1)), match.group(2)
        time_multipliers = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}
        return timedelta(**{time_multipliers[unit]: num})

    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        """Timeouts a user for a specified duration."""

        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member or not duration:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Usage: `,timeout @user 10m` (Use `s` for seconds, `m` for minutes, `h` for hours, `d` for days).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        duration_td = self.convert_time(duration)
        if duration_td is None:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Invalid duration format! Use `s`, `m`, `h`, `d`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout_for(duration_td, reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been timed out for **{duration}** by {ctx.author.mention}.",
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
        """Removes timeout from a user."""
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
            await member.timeout_until(None)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been untimed out by {ctx.author.mention}.",
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
        """Kicks a user from the server."""
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

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been kicked.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Bans a user from the server."""
        if not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Ban Members** permission to use this command.",
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
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to ban.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="unban")
    async def unban(self, ctx, user: discord.User = None):
        """Unbans a user from the server."""
        if not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Ban Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not user:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> You must mention a valid user to unban.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            bans = await ctx.guild.bans()
            banned_users = {ban_entry.user.id: ban_entry for ban_entry in bans}
            if user.id not in banned_users:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} <:cancel:1346853536738316339> This user is not banned.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            await ctx.guild.unban(user)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {user.mention} has been unbanned by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to unban.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
