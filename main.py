import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta

# BOT SETUP
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents)
bot.remove_command("help")  # Remove default help command

# KEEP BOT ONLINE
@tasks.loop(minutes=5)
async def keep_alive():
    print("Bot is running...")

@bot.event
async def on_ready():
    keep_alive.start()
    print(f'✅ Logged in as {bot.user}')

# TIMEOUT COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member = None, minutes: int = None, *, reason="No reason provided"):
    if not member or not minutes:
        embed = discord.Embed(
            title="⚠️ Error",
            description="You need to specify a user and the duration in minutes.\n\n**Example:** `,timeout @user 10`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    until = datetime.utcnow() + timedelta(minutes=minutes)
    await member.edit(timed_out_until=until, reason=reason)

    embed = discord.Embed(title="⏳ User Timed Out", color=discord.Color.orange())
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Duration", value=f"{minutes} minutes", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    await ctx.send(embed=embed)

# RUN BOT
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
