import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Kick Command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kicks a mentioned user from the guild."""

        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a valid user to kick.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Kick Server Owner",
                description="You cannot kick the **Server Owner**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                title="❌ Cannot Kick",
                description="You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to kick members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        await member.kick(reason=reason)

        embed = discord.Embed(
            title="✅ User Kicked",
            description=f"{member.mention} has been kicked from the server.\n**Reason:** {reason} <:currencypaw:1346100210899619901>",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # Timeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        """Mutes the provided member using Discord's timeout feature."""

        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a valid user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Timeout Server Owner",
                description="You cannot timeout the **Server Owner**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                title="❌ Cannot Timeout",
                description="You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to timeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not duration:
            embed = discord.Embed(
                title="⚠️ Duration Required",
                description="You must specify a duration for the timeout.\n\n**Example Usage:**\n`,timeout @user 10m` (10 minutes)",
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
                title="❌ Invalid Duration",
                description="Invalid time format! Use `s` (seconds), `m` (minutes), `h` (hours), or `d` (days).\n\n**Example:** `10m` for 10 minutes.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(timeout_duration, reason=f"Timed out by {ctx.author}: {reason}")
            embed = discord.Embed(
                title="✅ User Timed Out",
                description=f"{member.mention} has been timed out for **{duration}**.\n**Reason:** {reason} <:currencypaw:1346100210899619901>",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Action Failed",
                description="I was unable to timeout this user. Please check my permissions and try again.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Untimeout Command
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes the timeout from a provided member."""

        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a valid user to remove timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Remove Timeout",
                description="You cannot remove the timeout of the **Server Owner**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                title="❌ Cannot Remove Timeout",
                description="You cannot remove the timeout of someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to remove timeouts.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None, reason=f"Timeout removed by {ctx.author}")
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"{member.mention} is no longer timed out. <:currencypaw:1346100210899619901>",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Timeout removed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Action Failed",
                description="I was unable to remove the timeout. Please check my permissions and try again.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
