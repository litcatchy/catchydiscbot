import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Kick Command
    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kicks a member from the server."""
        
        # Manual permission check
        if not ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the **Kick Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

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
            description=f"{member.mention} has been kicked.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ✅ Timeout Command
    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        """Mutes a user using Discord's timeout feature."""
        
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a user to timeout.",
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

        if not duration:
            embed = discord.Embed(
                title="⚠️ Duration Required",
                description="Specify a duration (e.g., `10m`, `1h`).",
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
                description="Use `s` (seconds), `m` (minutes), `h` (hours), `d` (days).",
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

        try:
            await member.timeout(timeout_duration, reason=reason)
            embed = discord.Embed(
                title="✅ User Timed Out",
                description=f"{member.mention} timed out for **{duration}**.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Failed to Timeout",
                description=f"Error: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # ✅ Untimeout Command
    @commands.command()
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes the timeout from a user."""
        
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the **Timeout Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a user to remove their timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to untimeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"{member.mention} is no longer timed out.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Untimed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Failed to Remove Timeout",
                description=f"Error: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
