import discord
from discord.ext import commands, tasks
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents)

@tasks.loop(minutes=5)
async def keep_alive():
    pass  # Keeps the bot running

@bot.event
async def on_ready():
    keep_alive.start()

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
from collections import defaultdict
import discord
from discord.ext import commands
import asyncio

warns = defaultdict(list)  # Stores warnings as {user_id: [(reason, timestamp), ...]}

# TIMEOUT COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member = None, minutes: int = None, *, reason="No reason provided"):
    if not member or not minutes:
        embed = discord.Embed(title="⛔ Incorrect Usage", description="**Usage:** `,timeout @user time reason`", color=discord.Color.red())
        embed.set_footer(text="You must specify a user and time duration in minutes.")
        await ctx.send(embed=embed)
        return

    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)

    embed = discord.Embed(title="⏳ Timeout Issued", color=discord.Color.orange())
    embed.add_field(name="🔹 User", value=member.mention, inline=False)
    embed.add_field(name="⏱ Duration", value=f"{minutes} minutes", inline=False)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# KICK COMMAND
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if not member:
        embed = discord.Embed(title="⛔ Incorrect Usage", description="**Usage:** `,kick @user reason`", color=discord.Color.red())
        embed.set_footer(text="You must specify a user to kick.")
        await ctx.send(embed=embed)
        return

    await member.kick(reason=reason)

    embed = discord.Embed(title="🚪 User Kicked", color=discord.Color.red())
    embed.add_field(name="🔹 User", value=member.mention, inline=False)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# BAN COMMAND
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if not member:
        embed = discord.Embed(title="⛔ Incorrect Usage", description="**Usage:** `,ban @user reason`", color=discord.Color.red())
        embed.set_footer(text="You must specify a user to ban.")
        await ctx.send(embed=embed)
        return

    await member.ban(reason=reason)

    embed = discord.Embed(title="🔨 User Banned", color=discord.Color.dark_red())
    embed.add_field(name="🔹 User", value=member.mention, inline=False)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# WARN COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if not member:
        embed = discord.Embed(title="⛔ Incorrect Usage", description="**Usage:** `,warn @user reason`", color=discord.Color.red())
        embed.set_footer(text="You must specify a user to warn.")
        await ctx.send(embed=embed)
        return

    warns[member.id].append((reason, discord.utils.utcnow()))
    warn_count = len(warns[member.id])

    embed = discord.Embed(title="⚠️ Warning Issued", color=discord.Color.yellow())
    embed.add_field(name="🔹 User", value=member.mention, inline=False)
    embed.add_field(name="⚠️ Warning Count", value=warn_count, inline=False)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

    if warn_count >= 3:
        duration = discord.utils.utcnow() + discord.timedelta(minutes=30)
        await member.timeout(duration, reason="Exceeded 3 warnings")
        timeout_embed = discord.Embed(title="🚫 Auto Timeout", description=f"{member.mention} has been timed out for **30 minutes** due to **3 warnings**.", color=discord.Color.red())
        timeout_embed.set_footer(text="Warnings reset after timeout.")
        await ctx.send(embed=timeout_embed)
        warns[member.id] = []  # Reset warns after timeout

# CHECK WARNS COMMAND
@bot.command()
async def warns(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author  # If no user is mentioned, check own warns

    if member.id not in warns or len(warns[member.id]) == 0:
        embed = discord.Embed(title="✅ No Warnings", description=f"{member.mention} has no warnings.", color=discord.Color.green())
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=f"⚠️ Warnings for {member.name}", color=discord.Color.orange())
    for i, (reason, timestamp) in enumerate(warns[member.id], 1):
        embed.add_field(name=f"⚠️ Warning {i}", value=f"**Reason:** {reason} \n**Time:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", inline=False)

    await ctx.send(embed=embed)

# CLEAR WARNS COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def clearwarns(ctx, member: discord.Member = None):
    if not member:
        embed = discord.Embed(title="⛔ Incorrect Usage", description="**Usage:** `,clearwarns @user`", color=discord.Color.red())
        embed.set_footer(text="You must specify a user to clear their warnings.")
        await ctx.send(embed=embed)
        return

    warns[member.id] = []
    embed = discord.Embed(title="✅ Warnings Cleared", description=f"All warnings for {member.mention} have been cleared.", color=discord.Color.green())
    await ctx.send(embed=embed)
