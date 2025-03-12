import discord
from discord.ext import commands, tasks, menus
import asyncio
from database import Database

db = Database()
message_counts = {}

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clear_message_counts.start()

    def cog_unload(self):
        self.clear_message_counts.cancel()

    @tasks.loop(seconds=10)
    async def clear_message_counts(self):
        """Resets spam detection every 10 seconds."""
        global message_counts
        message_counts.clear()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Tracks message count and detects spam."""
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        db.update_messages(user_id)

        if user_id not in message_counts:
            message_counts[user_id] = 0
        message_counts[user_id] += 1

        if message_counts[user_id] > 5:
            embed = discord.Embed(
                description=f"<:currencypaw:1346100210899619901> **{message.author.mention}, stop spamming!**",
                color=discord.Color.red()
            )
            warning = await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            await warning.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Tracks voice chat time."""
        if before.channel is None and after.channel:
            self.bot.vc_timers[member.id] = asyncio.get_event_loop().time()
        elif before.channel and after.channel is None:
            if member.id in self.bot.vc_timers:
                joined_at = self.bot.vc_timers.pop(member.id)
                total_time = int(asyncio.get_event_loop().time() - joined_at)
                db.update_vc_time(member.id, total_time)

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        """Shows user message and VC stats."""
        member = member or ctx.author  
        messages_sent, vc_time = db.get_user_stats(member.id)

        embed = discord.Embed(title=f"<:currencypaw:1346100210899619901> Stats for {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="Total Messages Sent", value=f"{messages_sent:,}", inline=False)
        embed.add_field(name="Total VC Time", value=f"{vc_time // 3600}h {vc_time % 3600 // 60}m {vc_time % 60}s", inline=False)
        embed.set_thumbnail(url=member.avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="topchat")
    async def topchat(self, ctx):
        """Displays the top message senders."""
        top_chatters = db.get_top_chatters(limit=50)
        pages = [top_chatters[i:i+10] for i in range(0, len(top_chatters), 10)] or [[]]  

        class ChatMenu(menus.ListPageSource):
            async def format_page(self, menu, entries):
                embed = discord.Embed(title="<:currencypaw:1346100210899619901> Top Chat Users", color=discord.Color.blue())
                if not entries:
                    embed.description = "No data available."
                else:
                    embed.description = "\n".join(
                        f"**{i+1}. <@{user_id}>** **[{messages:,} messages]**"
                        for i, (user_id, messages) in enumerate(entries, start=menu.current_page * 10 + 1)
                    )
                return embed

        paginator = menus.MenuPages(source=ChatMenu(pages, per_page=1), clear_reactions_after=True)
        await paginator.start(ctx)

    @commands.command(name="topvc")
    async def topvc(self, ctx):
        """Displays the top VC users."""
        top_vc_users = db.get_top_vc(limit=50)
        pages = [top_vc_users[i:i+10] for i in range(0, len(top_vc_users), 10)] or [[]]  

        class VCMenu(menus.ListPageSource):
            async def format_page(self, menu, entries):
                embed = discord.Embed(title="<:currencypaw:1346100210899619901> Top VC Users", color=discord.Color.blue())
                if not entries:
                    embed.description = "No data available."
                else:
                    embed.description = "\n".join(
                        f"**{i+1}. <@{user_id}>** **[{vc_time // 3600}h {vc_time % 3600 // 60}m {vc_time % 60}s]**"
                        for i, (user_id, vc_time) in enumerate(entries, start=menu.current_page * 10 + 1)
                    )
                return embed

        paginator = menus.MenuPages(source=VCMenu(pages, per_page=1), clear_reactions_after=True)
        await paginator.start(ctx)

async def setup(bot):
    bot.vc_timers = {}  # Track VC join times
    await bot.add_cog(Leaderboard(bot))
