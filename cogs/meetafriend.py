import discord
from discord.ext import commands, tasks
import asyncio
import datetime

PANEL_CHANNEL_ID = 1358426717387096134
LOG_CHANNEL_ID = 1358430247628050554

class MeetAFriendView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="💌 Meet a friend", style=discord.ButtonStyle.primary, custom_id="meet_a_friend")
    async def meet_a_friend(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("MeetAFriend")
        await cog.handle_meet_a_friend(interaction)

    @discord.ui.button(label="Leave queue", style=discord.ButtonStyle.danger, custom_id="leave_queue")
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("MeetAFriend")
        await cog.handle_leave_queue(interaction)

class MeetAFriend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.waiting_queue = []
        self.active_threads = {}
        self.thread_activity = {}
        self.cleanup_inactive_threads.start()

    async def cog_load(self):
        # Add persistent view on cog load
        self.bot.add_view(MeetAFriendView(self.bot))

    @commands.hybrid_command(name="meetafriendpanel", description="Post the meet a friend panel.")
    async def meetafriendpanel(self, ctx):
        if ctx.channel.id != PANEL_CHANNEL_ID:
            return await ctx.reply("Please use this command in the correct channel.", ephemeral=True)

        embed = discord.Embed(
            title="💌 Meet a friend",
            description="Feeling shy and lonely? Chat individually\n\n"
                        "Want to chat one-on-one? Click below to get paired with someone.",
            color=discord.Color.pink()
        )
        embed.set_footer(text="discord.gg/lushie")

        view = MeetAFriendView(self.bot)
        await ctx.send(embed=embed, view=view)

    async def handle_meet_a_friend(self, interaction: discord.Interaction):
        user = interaction.user

        if user.id in self.waiting_queue:
            await interaction.response.send_message("You're already in the queue!", ephemeral=True)
            return

        for thread_info in self.active_threads.values():
            if user.id in thread_info['users']:
                await interaction.response.send_message("You're already in a chat!", ephemeral=True)
                return

        if not self.waiting_queue:
            self.waiting_queue.append(user.id)
            thread = await interaction.channel.create_thread(
                name=f"queue-{user.id}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )
            await thread.add_user(user)
            self.active_threads[thread.id] = {"users": [user.id], "queue": True}
            self.thread_activity[thread.id] = datetime.datetime.utcnow()
            embed = discord.Embed(
                title="Hang in tight 💌",
                description="You will find your pair soon!",
                color=discord.Color.pink()
            )
            await thread.send(embed=embed)
            await interaction.response.send_message("You've been added to the queue! Check your thread.", ephemeral=True)

            # Log
            await self.log_action(f"{user.mention} has entered the queue.")

        else:
            partner_id = self.waiting_queue.pop(0)
            partner = interaction.guild.get_member(partner_id)

            if not partner:
                await interaction.response.send_message("The previous user left the server. Try again!", ephemeral=True)
                return

            thread = await interaction.channel.create_thread(
                name=f"chat-{user.id}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )
            await thread.add_user(user)
            await thread.add_user(partner)

            self.active_threads[thread.id] = {"users": [user.id, partner.id], "queue": False}
            self.thread_activity[thread.id] = datetime.datetime.utcnow()

            embed = discord.Embed(
                title="You have been matched 💌",
                description=f"{partner.mention} and {user.mention} have been connected!",
                color=discord.Color.pink()
            )
            await thread.send(embed=embed)

            await interaction.response.send_message("You've been connected! Check your thread.", ephemeral=True)

            # Log
            await self.log_action(f"{partner.mention} and {user.mention} have been connected in {thread.mention}.")

    async def handle_leave_queue(self, interaction: discord.Interaction):
        user = interaction.user

        if user.id in self.waiting_queue:
            self.waiting_queue.remove(user.id)
            # Find and delete the user's queue thread
            for thread_id, info in list(self.active_threads.items()):
                if info['queue'] and user.id in info['users']:
                    thread = interaction.guild.get_thread(thread_id)
                    if thread:
                        await thread.delete(reason="User left the queue")
                    del self.active_threads[thread_id]
                    self.thread_activity.pop(thread_id, None)
            await interaction.response.send_message("You have left the queue.", ephemeral=True)
            await self.log_action(f"{user.mention} left the queue.")
            return

        # Check if user is in an active chat
        for thread_id, info in list(self.active_threads.items()):
            if not info['queue'] and user.id in info['users']:
                thread = interaction.guild.get_thread(thread_id)
                if thread:
                    await thread.delete(reason="User left the chat")
                del self.active_threads[thread_id]
                self.thread_activity.pop(thread_id, None)
                await interaction.response.send_message("You have left the chat.", ephemeral=True)
                await self.log_action(f"{user.mention} left the chat.")
                return

        await interaction.response.send_message("You are not in a queue or chat.", ephemeral=True)

    @tasks.loop(minutes=5)
    async def cleanup_inactive_threads(self):
        now = datetime.datetime.utcnow()
        for thread_id, last_activity in list(self.thread_activity.items()):
            if (now - last_activity).total_seconds() > 18000:  # 5 hours
                thread = self.bot.get_channel(thread_id)
                if thread:
                    await thread.delete(reason="Inactive thread cleanup")
                self.active_threads.pop(thread_id, None)
                self.thread_activity.pop(thread_id, None)

    @cleanup_inactive_threads.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    async def log_action(self, message: str):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(message)

async def setup(bot):
    await bot.add_cog(MeetAFriend(bot))
