import discord
from discord.ext import commands
import sqlite3
import asyncio
import os
from collections import defaultdict

# ✅ Ensure 'data' folder exists
os.makedirs("data", exist_ok=True)

# ✅ Database Class (Stores Message Counts & VC Time)
class Database:
    def __init__(self, db_path="data/stats.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates tables if they don't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                messages_sent INTEGER DEFAULT 0,
                vc_time INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def update_messages(self, user_id):
        """Increases message count (only counts once per 4 seconds)."""
        self.cursor.execute("""
            INSERT INTO user_stats (user_id, messages_sent)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET messages_sent = messages_sent + 1
        """, (user_id,))
        self.conn.commit()

    def update_vc_time(self, user_id, seconds):
        """Increases VC time (in seconds)."""
        self.cursor.execute("""
            INSERT INTO user_stats (user_id, vc_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET vc_time = vc_time + ?
        """, (user_id, seconds, seconds))
        self.conn.commit()

    def get_user_stats(self, user_id):
        """Gets stats for a specific user."""
        self.cursor.execute("SELECT messages_sent, vc_time FROM user_stats WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() or (0, 0)

    def get_top_chatters(self, limit=10):
        """Gets top users by message count."""
        self.cursor.execute("SELECT user_id, messages_sent FROM user_stats ORDER BY messages_sent DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def get_top_vc(self, limit=10):
        """Gets top users by VC time."""
        self.cursor.execute("SELECT user_id, vc_time FROM user_stats ORDER BY vc_time DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        self.conn.close()

# ✅ Load Database
db = Database()

# ✅ Spam Tracking (5 Messages in 10 Sec)
spam_tracker = defaultdict(list)

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Message Counter with Spam Protection
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        server_owner_id = message.guild.owner_id  # Get server owner ID

        # ✅ Track message timestamps
        spam_tracker[user_id].append(message.created_at.timestamp())

        # ✅ Remove messages older than 10 seconds
        spam_tracker[user_id] = [t for t in spam_tracker[user_id] if t > message.created_at.timestamp() - 10]

        # ✅ Spam Warning (Only if NOT Server Owner)
        if len(spam_tracker[user_id]) >= 5 and user_id != server_owner_id:
            embed = discord.Embed(
                description=f"<:currencypaw:1346100210899619901> **{message.author.mention}, stop spamming!**",
                color=discord.Color.red()
            )
            warning = await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            await warning.delete()

        # ✅ Update Database (only count once per 4 sec)
        last_msg_time = spam_tracker[user_id][-1] if spam_tracker[user_id] else 0
        if message.created_at.timestamp() - last_msg_time >= 4:
            db.update_messages(user_id)

    # ✅ User Stats Command
    @commands.command(name="lb")
    async def user_stats(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        messages_sent, vc_time = db.get_user_stats(member.id)

        embed = discord.Embed(
            title=f"📊 Stats for {member.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name="💬 Messages Sent", value=f"**{messages_sent}**", inline=True)
        embed.add_field(name="🎙️ VC Time", value=f"**{vc_time // 3600}h {vc_time % 3600 // 60}m {vc_time % 60}s**", inline=True)
        embed.set_footer(text="Leaderboard System")

        await ctx.send(embed=embed)

    # ✅ Top Chat Leaderboard Command
    @commands.command(name="topchat")
    async def top_chat(self, ctx):
        top_users = db.get_top_chatters(limit=10)

        embed = discord.Embed(title="🏆 Top Chatters", color=discord.Color.gold())
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

        for rank, (user_id, messages) in enumerate(top_users, start=1):
            user = ctx.guild.get_member(user_id)
            embed.add_field(name=f"#{rank} {user.display_name if user else 'Unknown'}", value=f"💬 **{messages} messages**", inline=False)

        await ctx.send(embed=embed)

    # ✅ Top VC Leaderboard Command
    @commands.command(name="topvc")
    async def top_vc(self, ctx):
        top_users = db.get_top_vc(limit=10)

        embed = discord.Embed(title="🎙️ Top VC Users", color=discord.Color.gold())
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

        for rank, (user_id, vc_time) in enumerate(top_users, start=1):
            user = ctx.guild.get_member(user_id)
            embed.add_field(name=f"#{rank} {user.display_name if user else 'Unknown'}", value=f"🕒 **{vc_time // 3600}h {vc_time % 3600 // 60}m {vc_time % 60}s**", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
