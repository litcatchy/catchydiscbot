import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = None):
        """Times out a user for a specified duration."""

        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You need the **Moderate Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not duration:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> Specify a duration (e.g., `10m`, `1h`).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            unit = duration[-1]
            if unit not in time_units:
                raise ValueError
            time_value = int(duration[:-1])
            timeout_duration = timedelta(seconds=time_value * time_units[unit])
        except (ValueError, TypeError):
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> Invalid duration. Use `s` (seconds), `m` (minutes), `h` (hours), `d` (days).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> I don’t have permission to timeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(timeout_duration, reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been timed out for **{duration}**.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes the timeout from a user."""
        
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You need the **Moderate Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to remove their timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> I don’t have permission to untimeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} is no longer timed out.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Untimed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = None):
        """Kicks a user from the server."""

        if not ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You need the **Kick Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to kick.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> I don’t have permission to kick members.",
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
            embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
