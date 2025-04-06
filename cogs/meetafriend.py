import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
from datetime import datetime, timedelta

class MeetAFriend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.threads = {}  # {user_id: thread}
        self.panel_message_id = None
        self.channel_id = 1358426717387096134  # Panel channel
        self.logs_channel_id = 1358430247628050554  # Logs channel
        self.check_inactivity.start()

    def cog_unload(self):
        self.check_inactivity.cancel()

    @commands.command(name="meetafriendpanel")
    async def meetafriendpanel(self, ctx):
        """Command to send the Meet a Friend panel."""
        if self.panel_message_id:
            await ctx.send("Panel already exists.")
            return

        channel = self.bot.get_channel(self.channel_id)

        embed = discord.Embed(
            title="💌 Meet a friend",
            description="Feeling shy and lonely? Chat individually\n"
                        "Want to chat one-on-one? Click below to get paired with someone.",
            color=discord.Color.pink()
        )
        embed.set_footer(text="discord.gg/lushie")

        view = discord.ui.View()
        view.add_item(MeetFriendButton(self))

        message = await channel.send(embed=embed, view=view)
        self.panel_message_id = message.id

        await ctx.send("Panel sent!")

    async def log(self, description):
        log_channel = self.bot.get_channel(self.logs_channel_id)
        embed = discord.Embed(
            title="Meet a Friend Logs",
            description=description,
            color=discord.Color.blurple()
        )
        await log_channel.send(embed=embed)

    async def create_or_get_thread(self, user):
        if user.id in self.threads:
            return self.threads[user.id]

        channel = self.bot.get_channel(self.channel_id)

        # Check for existing thread
        existing_thread = discord.utils.get(channel.threads, name=f"chat-{user.id}")
        if existing_thread:
            self.threads[user.id] = existing_thread
            return existing_thread

        # Create new private thread
        thread = await channel.create_thread(
            name=f"chat-{user.id}",
            type=discord.ChannelType.private_thread,
            auto_archive_duration=1440  # Max archive time
        )
        await thread.send(embed=discord.Embed(
            description="Hang in tight, you will find your pair soon 💌",
            color=discord.Color.pink()
        ))
        self.threads[user.id] = thread
        return thread

    async def match_users(self):
        while len(self.queue) >= 2:
            user1 = self.queue.pop(0)
            user2 = self.queue.pop(0)

            thread = await self.create_or_get_thread(user1)

            await thread.add_user(user2)

            embed = discord.Embed(
                description=f"You have been matched 💌\n"
                            f"{user1.mention} and {user2.mention} have been connected!",
                color=discord.Color.green()
            )
            await thread.send(embed=embed)

            await self.log(f"Matched {user1} with {user2} in thread {thread.name}")

    @tasks.loop(minutes=30)
    async def check_inactivity(self):
        now = datetime.utcnow()
        for thread in list(self.threads.values()):
            if thread.archived:
                continue
            messages = [msg async for msg in thread.history(limit=1)]
            if messages:
                last_message_time = messages[0].created_at
                if now - last_message_time > timedelta(hours=5):
                    await thread.delete()
                    await self.log(f"Deleted inactive thread {thread.name}")
                    # Remove users from queue and thread mapping
                    for user_id, t in list(self.threads.items()):
                        if t.id == thread.id:
                            del self.threads[user_id]

class MeetFriendButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="💌 Meet a friend", style=discord.ButtonStyle.primary)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user in self.cog.queue:
            await interaction.response.send_message("You are already in the queue!", ephemeral=True)
            return

        thread = await self.cog.create_or_get_thread(user)

        if user.id not in [u.id for u in thread.recipients]:
            await thread.add_user(user)

        self.cog.queue.append(user)
        await interaction.response.send_message("You've been added to the queue!", ephemeral=True)

        await self.cog.log(f"{user} joined the queue.")

        await self.cog.match_users()

        # Add Leave Queue button
        view = discord.ui.View()
        view.add_item(LeaveQueueButton(self.cog, user))
        await thread.send(view=view)

class LeaveQueueButton(discord.ui.Button):
    def __init__(self, cog, user):
        super().__init__(label="Leave Queue", style=discord.ButtonStyle.danger)
        self.cog = cog
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("This button isn't for you.", ephemeral=True)
            return

        if self.user in self.cog.queue:
            self.cog.queue.remove(self.user)
            await interaction.response.send_message("You have left the queue.", ephemeral=True)
            await self.cog.log(f"{self.user} left the queue.")
        elif self.user.id in self.cog.threads:
            thread = self.cog.threads[self.user.id]
            await thread.remove_user(self.user)
            await interaction.response.send_message("You have left the chat.", ephemeral=True)
            await self.cog.log(f"{self.user} left the chat thread {thread.name}.")
        else:
            await interaction.response.send_message("You are not in a queue or chat.", ephemeral=True)

def setup(bot):
    bot.add_cog(MeetAFriend(bot))
