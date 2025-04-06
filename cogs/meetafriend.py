import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta

LOG_CHANNEL_ID = 1358430247628050554
PANEL_CHANNEL_ID = 1358426717387096134
GUILD_ID = 1260272793883508757

class MeetAFriend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.waiting_user = None  # (user, thread)
        self.thread_activity = {}  # thread_id: last_activity datetime
        self.cleanup_inactive_threads.start()

    def cog_unload(self):
        self.cleanup_inactive_threads.cancel()

    @commands.command(name="meeta_friend_panel")
    async def meeta_friend_panel(self, ctx):
        if ctx.channel.id != PANEL_CHANNEL_ID:
            return await ctx.send("Please use this command in the correct channel.")

        embed = discord.Embed(
            title="💌 Meet a friend",
            description="Feeling shy and lonely? Chat individually\n\n"
                        "Want to chat one-on-one? Click below to get paired with someone.",
            color=discord.Color.pink()
        )
        embed.set_footer(text="discord.gg/lushie")

        view = MeetAFriendView(self)
        await ctx.send(embed=embed, view=view)

    @tasks.loop(minutes=10)
    async def cleanup_inactive_threads(self):
        now = datetime.utcnow()
        to_delete = []

        for thread_id, last_active in self.thread_activity.items():
            if now - last_active > timedelta(hours=5):
                to_delete.append(thread_id)

        for thread_id in to_delete:
            thread = self.bot.get_channel(thread_id)
            if thread:
                await thread.delete(reason="Inactive for 5 hours")
                await self.log_action(f"🧹 Thread `{thread.name}` deleted due to inactivity.")
            self.thread_activity.pop(thread_id, None)

    async def log_action(self, message):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(description=message, color=discord.Color.orange())
            await log_channel.send(embed=embed)

    async def update_activity(self, thread_id):
        self.thread_activity[thread_id] = datetime.utcnow()

class MeetAFriendView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.add_item(MeetAFriendButton(cog))
        self.add_item(LeaveButton(cog))

class MeetAFriendButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.primary, label="💌 Meet a friend")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        channel = interaction.channel

        # If user is already in queue, block
        if self.cog.waiting_user and self.cog.waiting_user[0].id == user.id:
            return await interaction.response.send_message("You are already in the queue!", ephemeral=True)

        # No one is waiting, create queue thread
        if self.cog.waiting_user is None:
            thread = await channel.create_thread(
                name=f"queue-{user.id}",
                type=discord.ChannelType.public_thread
            )
            await thread.add_user(user)
            await thread.send(embed=discord.Embed(
                description="💌 **Hang in tight, you will find your pair soon!**",
                color=discord.Color.pink()
            ))
            await interaction.response.send_message("You’ve been added to the queue 💌 Waiting for a friend. Note - inactive threads automatically gets deleted after 5 hours of inactivity.", ephemeral=True)

            self.cog.waiting_user = (user, thread)
            await self.cog.log_action(f"{user.mention} created a queue thread `{thread.name}`.")

            self.cog.thread_activity[thread.id] = datetime.utcnow()

        else:
            # Someone is waiting, create private chat thread
            waiting_user, queue_thread = self.cog.waiting_user

            chat_thread = await channel.create_thread(
                name=f"chat-{user.id}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )
            await chat_thread.add_user(user)
            await chat_thread.add_user(waiting_user)

            embed = discord.Embed(
                description=f"💌 **You have been matched!**\n\n{waiting_user.mention} and {user.mention} have been connected.",
                color=discord.Color.pink()
            )
            await chat_thread.send(embed=embed)

            await interaction.response.send_message(
                f"You've been connected with {waiting_user.mention}! Check your threads.",
                ephemeral=True
            )

            await self.cog.log_action(f"{waiting_user.mention} and {user.mention} connected in `{chat_thread.name}`.")

            self.cog.thread_activity[chat_thread.id] = datetime.utcnow()

            # Clean up old queue thread
            await queue_thread.delete()
            self.cog.thread_activity.pop(queue_thread.id, None)
            self.cog.waiting_user = None

class LeaveButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(style=discord.ButtonStyle.danger, label="🚪 Leave queue/chat")
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if user is the waiting user
        if self.cog.waiting_user and self.cog.waiting_user[0].id == user.id:
            thread = self.cog.waiting_user[1]
            await thread.delete(reason="User left the queue.")
            await interaction.response.send_message("You have left the queue.", ephemeral=True)
            await self.cog.log_action(f"{user.mention} left the queue and thread `{thread.name}` was deleted.")
            self.cog.thread_activity.pop(thread.id, None)
            self.cog.waiting_user = None
            return

        # Check if user is in any active thread
        for thread_id in list(self.cog.thread_activity.keys()):
            thread = self.cog.bot.get_channel(thread_id)
            if thread and user in thread.members:
                await thread.remove_user(user)
                await interaction.response.send_message("You have left the chat thread.", ephemeral=True)
                await self.cog.log_action(f"{user.mention} left the chat thread `{thread.name}`.")
                return

        await interaction.response.send_message("You are not in any queue or chat.", ephemeral=True)

@commands.Cog.listener()
async def on_message(message):
    if message.channel.id in [*MeetAFriend.thread_activity.keys()]:
        await MeetAFriend.update_activity(message.channel.id)

async def setup(bot):
    await bot.add_cog(MeetAFriend(bot))
