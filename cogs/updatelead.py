import discord
from discord.ext import commands
import asyncio
from database import Database

db = Database()

class UpdateLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vcm")
    async def update_vc_leaderboard(self, ctx, *, data: str):
        """Manually update VC leaderboard stats."""
        if ctx.author.id != 230022649844203522:  # Check if the user is the server owner
            embed = discord.Embed(
                title="<:currencypaw:1346100210899619901> Error",
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        lines = data.splitlines()
        for line in lines:
            try:
                parts = line.split()
                user_id = int(parts[0])
                vc_time = int(parts[1])

                # Update the VC time
                db.update_vc_time(user_id, vc_time)

            except Exception as e:
                embed = discord.Embed(
                    title="<:currencypaw:1346100210899619901> Error",
                    description=f"Error parsing data for line: {line}\nError: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                continue

        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> VC Leaderboard Stats Updated",
            description="The VC leaderboard stats have been successfully updated.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="chatm")
    async def update_chat_leaderboard(self, ctx, *, data: str):
        """Manually update chat leaderboard stats."""
        if ctx.author.id != 230022649844203522:  # Check if the user is the server owner
            embed = discord.Embed(
                title="<:currencypaw:1346100210899619901> Error",
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        lines = data.splitlines()
        for line in lines:
            try:
                parts = line.split()
                user_id = int(parts[0])
                messages_sent = int(parts[1])

                # Update the message count
                db.update_messages(user_id, messages_sent)

            except Exception as e:
                embed = discord.Embed(
                    title="<:currencypaw:1346100210899619901> Error",
                    description=f"Error parsing data for line: {line}\nError: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                continue

        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> Chat Leaderboard Stats Updated",
            description="The chat leaderboard stats have been successfully updated.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="5mlb")
    async def update_5min_leaderboard(self, ctx, *, data: str):
        """Manually updates the 5-minute leaderboard."""
        if ctx.author.id != 230022649844203522:  # Check if the user is the server owner
            embed = discord.Embed(
                title="<:currencypaw:1346100210899619901> Error",
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        lines = data.splitlines()
        for line in lines:
            try:
                parts = line.split()
                user_id = int(parts[0])
                messages_sent = int(parts[1])
                vc_time = int(parts[2])

                # Update the message count and VC time
                db.update_messages(user_id, messages_sent)
                db.update_vc_time(user_id, vc_time)

            except Exception as e:
                embed = discord.Embed(
                    title="<:currencypaw:1346100210899619901> Error",
                    description=f"Error parsing data for line: {line}\nError: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                continue

        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> 5-Minute Leaderboard Stats Updated",
            description="The leaderboard stats have been successfully updated.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UpdateLeaderboard(bot))
