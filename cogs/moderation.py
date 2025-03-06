import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = None):
        """Kicks the mentioned user from the guild."""

        # Check if the user has the required permission
        if not ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the **Kick Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Ensure a valid member is mentioned
        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a valid user to kick.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Prevent kicking the server owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Kick Server Owner",
                description="You cannot kick the **Server Owner**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member has a higher role
        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                title="❌ Cannot Kick",
                description="You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the bot has permission to kick
        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to kick members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Set default reason if none is provided
        if not reason:
            reason = "No reason provided"

        # Kick the member
        await member.kick(reason=reason)

        # Success message
        embed = discord.Embed(
            title="✅ User Kicked",
            description=f"{member.mention} has been kicked from the server.\n**Reason:** {reason} <:currencypaw:1346100210899619901>",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = None):
        """Mutes the provided member using Discord's timeout feature."""

        # Check if the user has the required permission
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the **Moderate Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Ensure a valid member is mentioned
        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a valid user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member exists in the server
        if member not in ctx.guild.members:
            embed = discord.Embed(
                title="⚠️ User Not Found",
                description="No user found with that name in this server. Kindly recheck and try again.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Prevent timing out the server owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Timeout Server Owner",
                description="You cannot timeout the **Server Owner**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member has a higher role
        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                title="❌ Cannot Timeout",
                description="You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Ensure a duration is provided
        if not duration:
            embed = discord.Embed(
                title="⚠️ Duration Required",
                description="You must specify a duration for the timeout.\n\n**Example Usage:**\n`,timeout @user 10m` (10 minutes)",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Convert duration to timedelta
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            unit = duration[-1]  # Get the last character (s, m, h, d)
            if unit not in time_units:
                raise ValueError
            time_value = int(duration[:-1])  # Extract the number part
            timeout_duration = timedelta(seconds=time_value * time_units[unit])
        except (ValueError, TypeError):
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Invalid time format! Use `s` (seconds), `m` (minutes), `h` (hours), or `d` (days).\n\n**Example:** `10m` for 10 minutes.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the bot has permission to timeout members
        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to timeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Set default reason if none is provided
        if not reason:
            reason = "No reason provided"

        # Apply the timeout
        try:
            await member.timeout(timeout_duration, reason=reason)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Timeout Failed",
                description=f"Failed to timeout {member.mention}.\nError: `{str(e)}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Success message
        embed = discord.Embed(
            title="✅ User Timed Out",
            description=f"{member.mention} has been **timed out** for `{duration}`.\n**Reason:** {reason} <:currencypaw:1346100210899619901>",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
  @commands.command()
    async def untimeout(self, ctx, member: discord.Member = None):
        """Removes the timeout from a provided member."""

        # Check if the user has the required permission
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the **Moderate Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Ensure a valid member is mentioned
        if not member:
            embed = discord.Embed(
                title="⚠️ Mention Required",
                description="You must mention a valid user to remove timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Prevent removing timeout from the server owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ Cannot Remove Timeout",
                description="You cannot remove the timeout of the **Server Owner**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member has a higher role
        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                title="❌ Cannot Remove Timeout",
                description="You cannot remove the timeout of someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the bot has permission to moderate members
        if not ctx.guild.me.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Bot Permissions",
                description="I don’t have permission to remove timeouts.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Remove the timeout
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


        
