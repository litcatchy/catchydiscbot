import discord
from discord.ext import commands, tasks
import asyncio
from collections import defaultdict
from database import Database
import time

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.message_counts = defaultdict(list)  # Spam tracking
        self.vc_times = defaultdict(int)  # Voice chat tracking
        self.track_vc_time.start()  # Starts tracking VC time

    def cog_unload(self):
        self.track_vc_time.cancel()  # Stop VC tracking on cog unload

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        user_id = message.author.id
        if message.guild and message.guild.owner_id == user_id:  # Ignore server owner
            return
        
        # Spam detection
        now = asyncio.get_event_loop().time()
        self.message_counts[user_id].append(now)
        self.message_counts[user_id] = [t for t in self.message_counts[user_id] if now - t < 10]

        if len(self.message_counts[user_id]) >= 5:
            embed = discord.Embed(
                description=f"<:currencypaw:1346100210899619901> **{message.author.mention}, stop spamming!**",
                color=discord.Color.red()
            )
            warning_msg = await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            await warning_msg.delete()

        # Update messages count (counts once per 4 sec)
        last_message_time = getattr(message.author, "last_message_time", 0)
        if now - last_message_time >= 4:
            self.db.update_messages(user_id)
            message.author.last_message_time = now  # Update last message time

    @tasks.loop(seconds=1)
    async def track_vc_time(self):
        """Tracks VC time every second"""
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if not member.bot:
                        self.db.update_vc_time(member.id, 1)

    @commands.command()
    async def stats(self, ctx, member: discord.Member = None):
        """Shows user stats: Messages sent & VC time"""
        member = member or ctx.author
        messages_sent, vc_time = self.db.get_user_stats(member.id)
        hours, remainder = divmod(vc_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title=f"Stats for {member.display_name}",
            description=(
                f"<:currencypaw:1346100210899619901> **Messages Sent:** {messages_sent}\n"
                f"<:currencypaw:1346100210899619901> **Voice Chat Time:** {hours} Hours {minutes} Minutes {seconds} Seconds"
            ),
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def topchat(self, ctx):
        """Leaderboard for top chatters"""
        top_chatters = self.db.get_top_chatters(10)
        if not top_chatters:
            return await ctx.send(embed=discord.Embed(description="<:currencypaw:1346100210899619901> No data found.", color=discord.Color.red()))

        description = "\n".join(
            f"**{idx+1}. <@{user_id}> - [{messages_sent}]**"
            for idx, (user_id, messages_sent) in enumerate(top_chatters)
        )

        embed = discord.Embed(title="🏆 Top Chatters 🏆", description=description, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @commands.command()
    async def topvc(self, ctx):
        """Leaderboard for top VC users"""
        top_vc_users = self.db.get_top_vc(10)
        if not top_vc_users:
            return await ctx.send(embed=discord.Embed(description="<:currencypaw:1346100210899619901> No data found.", color=discord.Color.red()))

        description = "\n".join(
            f"**{idx+1}. <@{user_id}> - [{vc_time // 3600} Hours {(vc_time % 3600) // 60} Minutes {vc_time % 60} Seconds]**"
            for idx, (user_id, vc_time) in enumerate(top_vc_users)
        )

        embed = discord.Embed(title="🎤 Top Voice Users 🎤", description=description, color=discord.Color.gold())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
