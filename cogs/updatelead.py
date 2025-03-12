import discord
from discord.ext import commands
from database import Database

db = Database()

class UpdateLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        """Check if the command author is the server owner."""
        async def predicate(ctx):
            return ctx.author.id == 230022649844203522  # Replace with your server owner's user ID
        return commands.check(predicate)

    @commands.command(name="vcm")
    @is_owner()
    async def modify_vc_leaderboard(self, ctx, *, data: str):
        """Modify VC leaderboard stats."""
        # Parse the data
        user_data = data.split("\n")
        for line in user_data:
            if line.strip():
                parts = line.split(" ")
                try:
                    user_id = int(parts[0])
                    messages_sent = int(parts[1])
                    vc_time = int(parts[2])

                    # Update the database with the new VC stats
                    db.update_messages(user_id, messages_sent)
                    db.update_vc_time(user_id, vc_time)
                except Exception as e:
                    await ctx.send(f"Error parsing data for line: {line}. Error: {str(e)}")
                    continue

        await ctx.send("VC leaderboard stats updated successfully.")

    @commands.command(name="chatm")
    @is_owner()
    async def modify_chat_leaderboard(self, ctx, *, data: str):
        """Modify chat leaderboard stats."""
        # Parse the data
        user_data = data.split("\n")
        for line in user_data:
            if line.strip():
                parts = line.split(" ")
                try:
                    user_id = int(parts[0])
                    messages_sent = int(parts[1])

                    # Update the database with the new message count
                    db.update_messages(user_id, messages_sent)
                except Exception as e:
                    await ctx.send(f"Error parsing data for line: {line}. Error: {str(e)}")
                    continue

        await ctx.send("Chat leaderboard stats updated successfully.")

    @commands.command(name="5mlb")
    @is_owner()
    async def modify_5minute_leaderboard(self, ctx, *, data: str):
        """Modify the 5-minute leaderboard stats sent by the bot."""
        # Parse the data
        user_data = data.split("\n")
        for line in user_data:
            if line.strip():
                parts = line.split(" ")
                try:
                    user_id = int(parts[0])
                    messages_sent = int(parts[1])
                    vc_time = int(parts[2])

                    # Update the database with the new 5-minute leaderboard stats
                    db.update_messages(user_id, messages_sent)
                    db.update_vc_time(user_id, vc_time)
                except Exception as e:
                    await ctx.send(f"Error parsing data for line: {line}. Error: {str(e)}")
                    continue

        await ctx.send("5-minute leaderboard stats updated successfully.")

async def setup(bot):
    await bot.add_cog(UpdateLeaderboard(bot))
