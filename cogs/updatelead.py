import discord
from discord.ext import commands
from database import Database

db = Database()

class UpdateLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, title, description, color):
        """Helper method to send an embed message."""
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="vcm")
    async def modify_vc_leaderboard(self, ctx, *, data):
        """Modify VC leaderboard stats for a user (Only server owner)."""
        if ctx.author.id != 230022649844203522:
            await self.send_embed(ctx, "Permission Denied", "You do not have permission to use this command.", discord.Color.red())
            return
        
        try:
            # Split the data into individual lines, then process each line
            lines = data.split("\n")
            for line in lines:
                parts = line.split()
                
                # Ensure there's at least one value for messages_sent and set vc_time to 0 if missing
                user_id = int(parts[0])
                messages_sent = int(parts[1])
                vc_time = int(parts[2]) if len(parts) > 2 else 0  # Default to 0 if VC time is missing

                # Update the VC stats for the user
                db.update_vc_time(user_id, vc_time)
                db.update_messages(user_id, messages_sent)
            
            await self.send_embed(ctx, "Leaderboard Update", "VC Leaderboard stats updated successfully.", discord.Color.green())
        except Exception as e:
            await self.send_embed(ctx, "Error", f"Error parsing data: {e}", discord.Color.red())

    @commands.command(name="chatm")
    async def modify_chat_leaderboard(self, ctx, *, data):
        """Modify chat leaderboard stats for a user (Only server owner)."""
        if ctx.author.id != 230022649844203522:
            await self.send_embed(ctx, "Permission Denied", "You do not have permission to use this command.", discord.Color.red())
            return
        
        try:
            # Split the data into individual lines, then process each line
            lines = data.split("\n")
            for line in lines:
                parts = line.split()
                
                # Ensure there's at least one value for messages_sent and set vc_time to 0 if missing
                user_id = int(parts[0])
                messages_sent = int(parts[1])
                vc_time = int(parts[2]) if len(parts) > 2 else 0  # Default to 0 if VC time is missing

                # Update the message stats for the user
                db.update_messages(user_id, messages_sent)
                db.update_vc_time(user_id, vc_time)
            
            await self.send_embed(ctx, "Leaderboard Update", "Chat Leaderboard stats updated successfully.", discord.Color.green())
        except Exception as e:
            await self.send_embed(ctx, "Error", f"Error parsing data: {e}", discord.Color.red())

    @commands.command(name="5mlb")
    async def modify_5min_leaderboard(self, ctx, *, data):
        """Modify 5-minute leaderboard stats for a user (Only server owner)."""
        if ctx.author.id != 230022649844203522:
            await self.send_embed(ctx, "Permission Denied", "You do not have permission to use this command.", discord.Color.red())
            return
        
        try:
            # Split the data into individual lines, then process each line
            lines = data.split("\n")
            for line in lines:
                parts = line.split()
                
                # Ensure there's at least one value for messages_sent and set vc_time to 0 if missing
                user_id = int(parts[0])
                messages_sent = int(parts[1])
                vc_time = int(parts[2]) if len(parts) > 2 else 0  # Default to 0 if VC time is missing

                # Update the message stats and VC stats for the user
                db.update_messages(user_id, messages_sent)
                db.update_vc_time(user_id, vc_time)
            
            await self.send_embed(ctx, "Leaderboard Update", "5-minute Leaderboard stats updated successfully.", discord.Color.green())
        except Exception as e:
            await self.send_embed(ctx, "Error", f"Error parsing data: {e}", discord.Color.red())

async def setup(bot):
    await bot.add_cog(UpdateLeaderboard(bot))
