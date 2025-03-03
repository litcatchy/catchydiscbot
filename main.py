import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta

# Load warnings from JSON file
def load_warnings():
    try:
        with open("warnings.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save warnings to JSON file
def save_warnings():
    with open("warnings.json", "w") as f:
        json.dump(warnings, f, indent=4)

warnings = load_warnings()

# Load user balances
def load_balances():
    try:
        with open("balances.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save user balances
def save_balances():
    with open("balances.json", "w") as f:
        json.dump(balances, f, indent=4)

balances = load_balances()

# Daily claim cooldown tracker
daily_claims = {}

# BOT SETUP
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents)
bot.remove_command("help")  # Remove default help command

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

# DAILY COMMAND WITH 24-HOUR COOLDOWN
@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    now = datetime.utcnow()

    if user_id in daily_claims:
        last_claim = daily_claims[user_id]
        if (now - last_claim).total_seconds() < 86400:  # 24 hours
            await ctx.send("You can only claim your daily reward once every 24 hours!")
            return

    amount = random.randint(100, 300)
    balances[user_id] = balances.get(user_id, 0) + amount
    daily_claims[user_id] = now
    save_balances()

    embed = discord.Embed(title="Daily Reward", color=0x00FF00)
    embed.add_field(name="Amount Received", value=f"<:currencypaw:1346100210899619901> {amount}", inline=False)
    embed.add_field(name="Next Claim", value="In 24 hours", inline=False)
    await ctx.send(embed=embed)

# LEADERBOARD COMMAND
@bot.command()
async def leaderboard(ctx):
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    description = "\n".join([f"{i+1}. <@{user}> - <:currencypaw:1346100210899619901> {balance}" for i, (user, balance) in enumerate(sorted_balances[:10])])
    embed = discord.Embed(title="Lushis Leaderboard", description=description, color=0xFFD700)
    await ctx.send(embed=embed)

# GIVE COMMAND
@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    giver_id = str(ctx.author.id)
    receiver_id = str(member.id)

    if amount <= 0 or giver_id == receiver_id or balances.get(giver_id, 0) < amount:
        await ctx.send("Invalid transaction.")
        return

    balances[giver_id] -= amount
    balances[receiver_id] = balances.get(receiver_id, 0) + amount
    save_balances()
    await ctx.send(f"{ctx.author.mention} gave {member.mention} <:currencypaw:1346100210899619901> {amount}.")

# ADMIN COMMANDS TO GIVE/TAKE LUSHIS
@commands.has_permissions(administrator=True)
@bot.command()
async def admin_give(ctx, member: discord.Member, amount: int):
    receiver_id = str(member.id)
    balances[receiver_id] = balances.get(receiver_id, 0) + amount
    save_balances()
    await ctx.send(f"Admin gave {member.mention} <:currencypaw:1346100210899619901> {amount}.")

@commands.has_permissions(administrator=True)
@bot.command()
async def admin_take(ctx, member: discord.Member, amount: int):
    receiver_id = str(member.id)
    balances[receiver_id] = max(0, balances.get(receiver_id, 0) - amount)
    save_balances()
    await ctx.send(f"Admin took <:currencypaw:1346100210899619901> {amount} from {member.mention}.")

# RUN BOT
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
