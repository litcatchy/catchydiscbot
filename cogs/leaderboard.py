import discord
from discord.ext import commands
import sqlite3
import asyncio

class Database:
    def __init__(self, db_path="data/stats.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                messages_sent INTEGER DEFAULT 0,
                vc_time INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def update_messages(self, user_id):
        self.cursor.execute("""
            INSERT INTO user_stats (user_id, messages_sent)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET messages_sent = messages_sent + 1
        """, (user_id,))
        self.conn.commit()

    def update_vc_time(self, user_id, seconds):
        self.cursor.execute("""
            INSERT INTO user_stats (user_id, vc_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET vc_time = vc_time + ?
        """, (user_id, seconds, seconds))
        self.conn.commit()

    def get_user_stats(self, user_id):
        self.cursor.execute("SELECT messages_sent, vc_time FROM user_stats WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() or (0, 0)

    def get_top_chatters(self, limit=50):
        self.cursor.execute("SELECT user_id, messages_sent FROM user_stats ORDER BY messages_sent DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def get_top_vc(self, limit=50):
        self.cursor.execute("SELECT user_id, vc_time FROM user_stats ORDER BY vc_time DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

db = Database()

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_count = {}  # Tracks last message time for spam warning
        self.vc_tracking = {}  # Tracks when users join VC

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        db.update_messages(user_id)

        # Spam Warning System
        if message.author.id in self.message_count:
            self.message_count[user_id].append(message.created_at.timestamp())
        else:
            self.message_count[user_id] = [message.created_at.timestamp()]

        self.message_count[user_id] = [t for t in self.message_count[user_id] if t > message.created_at.timestamp() - 10]

        if len(self.message_count[user_id]) >= 5 and message.author.id != message.guild.owner_id:
            embed = discord.Embed(
                description=f"<:currencypaw:1346100210899619901> **{message.author.mention}, stop spamming!**",
                color=discord.Color.red()
            )
            msg = await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            await msg.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        user_id = member.id

        if after.channel and not before.channel:
            self.vc_tracking[user_id] = asyncio.get_event_loop().time()
        elif before.channel and not after.channel and user_id in self.vc_tracking:
            time_spent = asyncio.get_event_loop().time() - self.vc_tracking[user_id]
            db.update_vc_time(user_id, int(time_spent))
            del self.vc_tracking[user_id]

    @commands.command(name="stats")
    async def user_stats(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        messages_sent, vc_time = db.get_user_stats(member.id)

        hours, remainder = divmod(vc_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        vc_time_formatted = f"{hours}h {minutes}m {seconds}s"

        embed = discord.Embed(title=f"Stats for {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="Messages Sent", value=f"{messages_sent}", inline=True)
        embed.add_field(name="VC Time", value=f"{vc_time_formatted}", inline=True)
        embed.set_footer(text="Leaderboard System")
        await ctx.send(embed=embed)

    @commands.command(name="topchat")
    async def top_chat(self, ctx):
        top_users = db.get_top_chatters()
        pages = [top_users[i:i+10] for i in range(0, len(top_users), 10)]
        page_num = 0

        async def update_embed(interaction, page_num):
            embed = discord.Embed(title="Top Chatters", color=discord.Color.gold())
            for idx, (user_id, messages) in enumerate(pages[page_num], start=page_num * 10 + 1):
                user = self.bot.get_user(user_id)
                embed.add_field(name=f"#{idx} {user.display_name if user else 'Unknown'}", value=f"{messages} messages", inline=False)
            embed.set_footer(text=f"Page {page_num + 1} of {len(pages)}")
            await interaction.response.edit_message(embed=embed)

        embed = discord.Embed(title="Top Chatters", color=discord.Color.gold())
        for idx, (user_id, messages) in enumerate(pages[page_num], start=1):
            user = self.bot.get_user(user_id)
            embed.add_field(name=f"#{idx} {user.display_name if user else 'Unknown'}", value=f"{messages} messages", inline=False)
        embed.set_footer(text=f"Page {page_num + 1} of {len(pages)}")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.gray, custom_id="prev"))
        view.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.gray, custom_id="next"))

        msg = await ctx.send(embed=embed, view=view)

        async def button_callback(interaction):
            nonlocal page_num
            if interaction.data["custom_id"] == "next" and page_num < len(pages) - 1:
                page_num += 1
            elif interaction.data["custom_id"] == "prev" and page_num > 0:
                page_num -= 1
            await update_embed(interaction, page_num)

        for button in view.children:
            button.callback = button_callback

    @commands.command(name="topvc")
    async def top_vc(self, ctx):
        top_users = db.get_top_vc()
        pages = [top_users[i:i+10] for i in range(0, len(top_users), 10)]
        page_num = 0

        async def update_embed(interaction, page_num):
            embed = discord.Embed(title="Top VC Users", color=discord.Color.blue())
            for idx, (user_id, vc_time) in enumerate(pages[page_num], start=page_num * 10 + 1):
                user = self.bot.get_user(user_id)
                embed.add_field(name=f"#{idx} {user.display_name if user else 'Unknown'}", value=f"{vc_time} seconds", inline=False)
            embed.set_footer(text=f"Page {page_num + 1} of {len(pages)}")
            await interaction.response.edit_message(embed=embed)

        embed = discord.Embed(title="Top VC Users", color=discord.Color.blue())
        for idx, (user_id, vc_time) in enumerate(pages[page_num], start=1):
            user = self.bot.get_user(user_id)
            embed.add_field(name=f"#{idx} {user.display_name if user else 'Unknown'}", value=f"{vc_time} seconds", inline=False)
        embed.set_footer(text=f"Page {page_num + 1} of {len(pages)}")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.gray, custom_id="prev"))
        view.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.gray, custom_id="next"))

        msg = await ctx.send(embed=embed, view=view)

        async def button_callback(interaction):
            nonlocal page_num
            if interaction.data["custom_id"] == "next" and page_num < len(pages) - 1:
                page_num += 1
            elif interaction.data["custom_id"] == "prev" and page_num > 0:
                page_num -= 1
            await update_embed(interaction, page_num)

        for button in view.children:
            button.callback = button_callback

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
