import discord from discord.ext import commands, tasks import asyncio from datetime import datetime, timedelta

Your emojis

MEET_EMOJI = '<:ios_emoji58:1358438461732028560>' LEAVE_EMOJI = '<:leave:1358438625280524348>'

Channel and log channel IDs

PANEL_CHANNEL_ID = 1358426717387096134 LOG_CHANNEL_ID = 1358430247628050554

class MeetAFriend(commands.Cog): def init(self, bot): self.bot = bot self.queue = [] self.active_threads = {} self.last_activity = {} self.cleanup_threads.start()

@commands.command(name='meetafriendpanel')
async def meet_a_friend_panel(self, ctx):
    if ctx.channel.id != PANEL_CHANNEL_ID:
        return

    embed = discord.Embed(
        title=f'{MEET_EMOJI} Meet a friend',
        description='Feeling shy and lonely? Chat individually\nWant to chat one-on-one? Click below to get paired with someone.',
        color=discord.Color.blurple()
    )
    embed.set_footer(text='discord.gg/lushie')

    view = discord.ui.View()
    view.add_item(MeetButton(self))
    view.add_item(LeaveButton(self))

    await ctx.send(embed=embed, view=view)

async def create_thread(self, user):
    panel_channel = self.bot.get_channel(PANEL_CHANNEL_ID)

    existing_thread = discord.utils.get(panel_channel.threads, name="chat")
    if existing_thread:
        thread = existing_thread
    else:
        thread = await panel_channel.create_thread(
            name="chat",
            type=discord.ChannelType.private_thread
        )

    await thread.add_user(user)
    self.last_activity[thread.id] = datetime.utcnow()
    return thread

async def log(self, message):
    log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(
        description=message,
        color=discord.Color.green()
    )
    await log_channel.send(embed=embed)

async def handle_queue(self, interaction):
    user = interaction.user

    # If user already in queue or in active chat
    for u1, u2 in self.active_threads.values():
        if user.id in (u1.id, u2.id):
            await interaction.response.send_message("You are already in a chat.", ephemeral=True)
            return

    if user.id in self.queue:
        await interaction.response.send_message("You are already in the queue.", ephemeral=True)
        return

    self.queue.append(user.id)
    thread = await self.create_thread(user)
    await thread.send(embed=discord.Embed(description=f"Hang in tight you will find your pair soon {MEET_EMOJI}"))

    await self.log(f"{user.mention} has joined the queue.")
    await interaction.response.send_message("You have been added to the queue", ephemeral=True)

    # Matchmaking
    if len(self.queue) >= 2:
        user1_id = self.queue.pop(0)
        user2_id = self.queue.pop(0)

        user1 = await self.bot.fetch_user(user1_id)
        user2 = await self.bot.fetch_user(user2_id)

        thread = await self.create_thread(user1)
        await thread.add_user(user2)

        self.active_threads[thread.id] = (user1, user2)
        self.last_activity[thread.id] = datetime.utcnow()

        embed = discord.Embed(
            description=f'You have been matched {MEET_EMOJI}\n{user1.mention} and {user2.mention} have been connected.',
            color=discord.Color.green()
        )
        await thread.send(embed=embed)
        await self.log(f"{user1.mention} and {user2.mention} have been connected in {thread.mention}.")

async def handle_leave(self, interaction):
    user = interaction.user

    if user.id in self.queue:
        self.queue.remove(user.id)
        await self.log(f"{user.mention} left the queue.")
        await interaction.response.send_message("You have left the queue.", ephemeral=True)
        return

    for thread_id, (user1, user2) in list(self.active_threads.items()):
        if user.id in (user1.id, user2.id):
            thread = self.bot.get_channel(thread_id)
            if thread:
                await thread.send(embed=discord.Embed(description=f"{user.mention} has left the chat."))
                await thread.remove_user(user1)
                await thread.remove_user(user2)
                await thread.edit(archived=True)
                await self.log(f"{user.mention} left the chat {thread.mention}.")
            del self.active_threads[thread_id]
            del self.last_activity[thread_id]
            await interaction.response.send_message("You have left the chat.", ephemeral=True)
            return

    await interaction.response.send_message("You are not in a queue or chat.", ephemeral=True)

@tasks.loop(minutes=30)
async def cleanup_threads(self):
    now = datetime.utcnow()
    for thread_id, last_active in list(self.last_activity.items()):
        if now - last_active > timedelta(hours=5):
            thread = self.bot.get_channel(thread_id)
            if thread:
                await thread.send(embed=discord.Embed(description="This chat has been inactive for 5 hours and will be closed."))
                await thread.edit(archived=True)
                await self.log(f"Archived inactive thread {thread.mention}.")
            self.active_threads.pop(thread_id, None)
            self.last_activity.pop(thread_id, None)

@cleanup_threads.before_loop
async def before_cleanup(self):
    await self.bot.wait_until_ready()

class MeetButton(discord.ui.Button): def init(self, cog): super().init(label=f'Meet a friend {MEET_EMOJI}', style=discord.ButtonStyle.blurple) self.cog = cog

async def callback(self, interaction: discord.Interaction):
    await self.cog.handle_queue(interaction)

class LeaveButton(discord.ui.Button): def init(self, cog): super().init(label=f'Leave {LEAVE_EMOJI}', style=discord.ButtonStyle.red) self.cog = cog

async def callback(self, interaction: discord.Interaction):
    await self.cog.handle_leave(interaction)

async def setup(bot): await bot.add_cog(MeetAFriend(bot))

