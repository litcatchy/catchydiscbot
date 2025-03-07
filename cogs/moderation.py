import discord
from discord.ext import commands
import re
from datetime import timedelta

class Moderation(commands.Cog):
    """Moderation commands for managing users."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a user from the server."""
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban that user.")
        except discord.HTTPException:
            await ctx.send("An error occurred while trying to ban that user.")

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a user from the server."""
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick that user.")
        except discord.HTTPException:
            await ctx.send("An error occurred while trying to kick that user.")

    @commands.command()
    async def timeout(self, ctx, member: discord.Member, time: str):
        """Timeout a user for a specified amount of time."""

        # Parse the time input using regex (e.g., 10m, 1h, 30s)
        match = re.match(r"(\d+)([smh])", time)

        if not match:
            await ctx.send("Invalid time format. Please use a format like `10m`, `1h`, or `30s`.")
            return

        amount, unit = match.groups()

        try:
            amount = int(amount)

            # Convert the time to seconds
            if unit == "m":
                duration = timedelta(minutes=amount)
            elif unit == "h":
                duration = timedelta(hours=amount)
            elif unit == "s":
                duration = timedelta(seconds=amount)
            else:
                await ctx.send("Invalid unit. Use `m` for minutes, `h` for hours, and `s` for seconds.")
                return

            # Apply the timeout to the member
            await member.timeout(duration)

            await ctx.send(f"{member.mention} has been timed out for {time}.")

        except ValueError:
            await ctx.send("Invalid number for timeout duration.")
        except discord.DiscordException as e:
            await ctx.send(f"Error: {str(e)}")

    @commands.command()
    async def untimeout(self, ctx, member: discord.Member):
        """Untimeout a user."""
        # Check if the user is currently timed out
        if member.is_timed_out():
            # Remove the timeout
            await member.timeout(None)
            await ctx.send(f"Successfully untimed out {member.mention}.")
        else:
            await ctx.send(f"{member.mention} is not currently timed out.")

    @commands.command()
    async def unban(self, ctx, user_id: int):
        """Unban a user by their ID."""
        try:
            # Try to unban the user
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"Successfully unbanned {user.mention}.")
        except discord.NotFound:
            await ctx.send("User is not banned.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to unban that user.")
        except discord.HTTPException:
            await ctx.send("An error occurred while trying to unban that user.")


# Setup function to add the cog
def setup(bot):
    bot.add_cog(Moderation(bot))
