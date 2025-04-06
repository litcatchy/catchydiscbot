import discord
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=',', intents=intents)

QUEUE = []
PANEL_CHANNEL_ID = 1358426717387096134
LOG_CHANNEL_ID = 1358430247628050554
THREAD_TIMEOUT_HOURS = 5
panel_message_id = None

class MeetAFriend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_threads = {}
        self.cleanup_threads.start()

    @commands.command(name="meetafriendpanel")
    async def meetafriendpanel(self, ctx):
        if ctx.channel.id != PANEL_CHANNEL_ID:
            return await ctx.send("Use this command in the correct channel.", delete_after=5)

        global panel_message_id

        # Check if panel already exists
        if panel_message_id:
            try:
                existing_message = await ctx.channel.fetch_message(panel_message_id)
                if existing_message:
                    return await ctx.send("Panel already exists!", delete_after=5)
            except discord.NotFound:
                pass  # Message deleted, continue to send new panel

        embed = discord.Embed(
            title="<:ios_emoji58:1358438461732028560> Meet a friend",
            description="Feeling shy and lonely? Chat individually\nWant to chat one-on-one? Click below to get paired with someone.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="discord.gg/lushie")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary,
            emoji="<:ios_emoji58:1358438461732028560>",
            label="Meet a friend",
            custom_id="meet_a_friend"
        ))
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="<:leave:1358438625280524348>",
            label="Leave",
            custom_id="leave_queue"
        ))

        message = await ctx.send(embed=embed, view=view)
        panel_message_id = message.id

    @tasks.loop(minutes=30)
    async def cleanup_threads(self):
        now = datetime.utcnow()
        to_delete = []
        for thread_id, last_active in list(self.active_threads.items()):
            if now - last_active > timedelta(hours=THREAD_TIMEOUT_HOURS):
                thread = self.bot.get_channel(thread_id)
                if thread:
                    await thread.delete(reason="Thread inactive for over 5 hours")
                    await self.log_embed(f"Deleted inactive thread: {thread.name}")
                to_delete.append(thread_id)
        for thread_id in to_delete:
            del self.active_threads[thread_id]

    async def log_embed(self, description):
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = discord.Embed(description=description, color=discord.Color.orange())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.component:
            return

        if interaction.data['custom_id'] == 'meet_a_friend':
            await interaction.response.defer(ephemeral=True)
            user = interaction.user

            # Check if user is already in queue
            if user.id in QUEUE:
                await interaction.followup.send("You're already in the queue!", ephemeral=True)
                return

            # Check for existing thread
            existing_thread = discord.utils.get(interaction.channel.threads, name=f"chat")
            if existing_thread:
                await interaction.followup.send("A chat is already in progress.", ephemeral=True)
                return

            # Add user to queue
            QUEUE.append(user.id)
            await self.log_embed(f"{user.mention} joined the queue.")

            if len(QUEUE) >= 2:
                user1_id = QUEUE.pop(0)
                user2_id = QUEUE.pop(0)

                user1 = interaction.guild.get_member(user1_id)
                user2 = interaction.guild.get_member(user2_id)

                # Create private thread
                thread = await interaction.channel.create_thread(
                    name=f"chat",
                    type=discord.ChannelType.private_thread,
                    invitable=False
                )
                await thread.add_user(user1)
                await thread.add_user(user2)

                self.active_threads[thread.id] = datetime.utcnow()

                # Send matched message
                embed = discord.Embed(
                    description=f"You have been matched! <:ios_emoji58:1358438461732028560>\n{user1.mention} and {user2.mention} have been connected.",
                    color=discord.Color.green()
                )
                await thread.send(embed=embed)
                await self.log_embed(f"{user1.mention} and {user2.mention} have been connected in {thread.mention}.")
            else:
                # Create thread for single user
                thread = await interaction.channel.create_thread(
                    name=f"chat",
                    type=discord.ChannelType.private_thread,
                    invitable=False
                )
                await thread.add_user(user)

                self.active_threads[thread.id] = datetime.utcnow()

                embed = discord.Embed(
                    description="Hang in tight, you will find your pair soon! <:ios_emoji58:1358438461732028560>",
                    color=discord.Color.blurple()
                )
                await thread.send(embed=embed)
                await self.log_embed(f"{user.mention} is waiting for a match in {thread.mention}.")

        elif interaction.data['custom_id'] == 'leave_queue':
            await interaction.response.defer(ephemeral=True)
            user = interaction.user
            if user.id in QUEUE:
                QUEUE.remove(user.id)
                await interaction.followup.send("You have left the queue.", ephemeral=True)
                await self.log_embed(f"{user.mention} left the queue.")
            else:
                # Check if user is in any active thread
                for thread_id in list(self.active_threads):
                    thread = self.bot.get_channel(thread_id)
                    if thread and user in thread.members:
                        await thread.remove_user(user)
                        await self.log_embed(f"{user.mention} left the chat in {thread.mention}.")
                        await interaction.followup.send("You have left the chat.", ephemeral=True)
                        return
                await interaction.followup.send("You're not in any queue or chat.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.active_threads:
            self.active_threads[message.channel.id] = datetime.utcnow()

def setup(bot):
    bot.add_cog(MeetAFriend(bot))
