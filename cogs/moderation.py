import discord
from discord.ext import commands
import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def convert_time(self, time_str):
        """Converts a time string (e.g., '10m', '2h') into seconds."""
        match = re.match(r"^(\d+)([smhd])$", time_str)
        if not match:
            return None
        
        num, unit = int(match.group(1)), match.group(2)
        time_multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        return num * time_multipliers[unit]

    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> You must mention a user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not duration:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You must specify a duration. Example: `10m` (10 minutes), `1h` (1 hour), `30s` (30 seconds), `2d` (2 days).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        duration_seconds = self.convert_time(duration)
        if duration_seconds is None:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Invalid duration format! Use `s` (seconds), `m` (minutes), `h` (hours), or `d` (days). Example: `10m` (10 minutes), `1h` (1 hour).",
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

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I do not have permission to timeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(duration_seconds, reason=reason)
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
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> You must mention a user to remove their timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been removed from timeout by {ctx.author.mention}.",
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
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = None):
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

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been kicked by {ctx.author.mention}.",
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
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.guild.owner:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
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

async def setup(bot):
    await bot.add_cog(Moderation(bot))
