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
        now = time.time()
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
        if not hasattr(message.author, "last_message_time"):
            message.author.last_message_time = 0

        if now - message.author.last_message_time >= 4:
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

class LeaderboardPaginator(discord.ui.View):
    def __init__(self, data, title, page_size=10):
        super().__init__()
        self.data = data
        self.title = title
        self.page_size = page_size
        self.current_page = 0

    async def send_initial_message(self, ctx):
        self.message = await ctx.send(embed=self.get_page(), view=self)

    def get_page(self):
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_data = self.data[start:end]

        if not page_data:
            description = "<:currencypaw:1346100210899619901> No data available."
        else:
            description = "\n".join(
                f"**{idx+1+start}. <@{user_id}> - [{value}]**"
                for idx, (user_id, value) in enumerate(page_data)
            )

        embed = discord.Embed(
            title=f"<:currencypaw:1346100210899619901> {self.title}",
            description=description,
            color=discord.Color.gold()
        )
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_page(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.current_page + 1) * self.page_size < len(self.data):
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_page(), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # Allows anyone to interact with the buttons

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_error(self, error, item, interaction):
        await interaction.response.send_message("An error occurred.", ephemeral=True)

    @commands.command()
    async def topchat(self, ctx):
        """Leaderboard for top chatters"""
        top_chatters = self.db.get_top_chatters(50)  # Get up to 50 users for pagination
        paginator = LeaderboardPaginator(top_chatters, "Top Chatters")
        await paginator.send_initial_message(ctx)

    @commands.command()
    async def topvc(self, ctx):
        """Leaderboard for top VC users"""
        top_vc_users = self.db.get_top_vc(50)  # Get up to 50 users for pagination
        paginator = LeaderboardPaginator(top_vc_users, "Top VC Users")
        await paginator.send_initial_message(ctx)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
