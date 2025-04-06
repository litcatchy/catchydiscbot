import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

class MeetAFriendView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="💌 Meet a friend", style=discord.ButtonStyle.primary, custom_id="meet_a_friend_button")
    async def meet_a_friend(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.bot.get_cog("MeetAFriend").handle_queue(interaction)

    @discord.ui.button(label="✋🏻 Leave queue", style=discord.ButtonStyle.danger, custom_id="leave_queue_button")
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.bot.get_cog("MeetAFriend").leave_queue(interaction)


class MeetAFriend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.active_threads = {}
        self.inactivity_check.start()

    def cog_unload(self):
        self.inactivity_check.cancel()

    @commands.command(name="meetafriendpanel")
    async def meetafriendpanel(self, ctx):
        embed = discord.Embed(
            title="💌 Meet a friend",
            description="Feeling shy and lonely? Chat individually\n"
                        "Want to chat one-on-one? Click below to get paired with someone.",
            color=discord.Color.pink()
        )
        embed.set_footer(text="discord.gg/lushie")
        view = MeetAFriendView(self.bot)
        channel = self.bot.get_channel(1358426717387096134)
        await channel.send(embed=embed, view=view)
        log_channel = self.bot.get_channel(1358430247628050554)

        log_embed = discord.Embed(
            description=f"Meet a friend panel has been posted in {channel.mention}.",
            color=discord.Color.blurple()
        )
        await log_channel.send(embed=log_embed)

    async def handle_queue(self, interaction: discord.Interaction):
        user = interaction.user

        # Already in queue or active chat check
        if user.id in self.active_threads:
            await interaction.followup.send("You are already in an active chat!", ephemeral=True)
            return
        if any(entry["user"].id == user.id for entry in self.queue):
            await interaction.followup.send("You are already in the queue!", ephemeral=True)
            return

        log_channel = self.bot.get_channel(1358430247628050554)

        if self.queue:
            # Match found
            partner_entry = self.queue.pop(0)
            partner = partner_entry["user"]
            channel = interaction.channel

            # Use existing thread and rename it
            thread = self.active_threads[partner.id]["thread"]
            await thread.edit(name=f"chat-{user.id}")

            await thread.add_user(user)

            embed = discord.Embed(
                title="💌 You have been matched!",
                description=f"{user.mention} and {partner.mention} have been connected.",
                color=discord.Color.green()
            )
            await thread.send(embed=embed)

            self.active_threads[user.id] = {"thread": thread, "partner": partner.id, "last_activity": datetime.utcnow()}
            self.active_threads[partner.id] = {"thread": thread, "partner": user.id, "last_activity": datetime.utcnow()}

            log_embed = discord.Embed(
                description=f"{user.mention} and {partner.mention} have been matched in thread {thread.mention}.",
                color=discord.Color.green()
            )
            await log_channel.send(embed=log_embed)

        else:
            # Add to queue
            self.queue.append({"user": user, "timestamp": datetime.utcnow()})
            thread = await interaction.channel.create_thread(
                name=f"queue-{user.id}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )
            await thread.add_user(user)

            embed = discord.Embed(
                description="Hang in tight, you will find your pair soon 💌",
                color=discord.Color.orange()
            )
            await thread.send(embed=embed)

            self.active_threads[user.id] = {"thread": thread, "partner": None, "last_activity": datetime.utcnow()}

            log_embed = discord.Embed(
                description=f"{user.mention} has joined the queue in thread {thread.mention}.",
                color=discord.Color.orange()
            )
            await log_channel.send(embed=log_embed)

    async def leave_queue(self, interaction: discord.Interaction):
        user = interaction.user
        log_channel = self.bot.get_channel(1358430247628050554)

        # Leave active chat
        if user.id in self.active_threads:
            thread_info = self.active_threads[user.id]
            thread = thread_info["thread"]
            partner_id = thread_info["partner"]

            await thread.send(f"{user.mention} has left the chat.")
            await thread.remove_user(user)

            if partner_id:
                partner = thread.guild.get_member(partner_id)
                if partner:
                    await thread.send(f"{partner.mention} you can leave the thread or wait for a new partner.")

            del self.active_threads[user.id]

            log_embed = discord.Embed(
                description=f"{user.mention} left the active chat in thread {thread.mention}.",
                color=discord.Color.red()
            )
            await log_channel.send(embed=log_embed)

            await interaction.followup.send("You have left the chat.", ephemeral=True)
            return

        # Leave queue
        for entry in self.queue:
            if entry["user"].id == user.id:
                self.queue.remove(entry)

                log_embed = discord.Embed(
                    description=f"{user.mention} left the queue.",
                    color=discord.Color.red()
                )
                await log_channel.send(embed=log_embed)

                await interaction.followup.send("You have left the queue.", ephemeral=True)
                return

        await interaction.followup.send("You are not in the queue or an active chat.", ephemeral=True)

    @tasks.loop(minutes=30)
    async def inactivity_check(self):
        now = datetime.utcnow()
        to_delete = []

        for user_id, info in list(self.active_threads.items()):
            last_activity = info["last_activity"]
            if (now - last_activity) > timedelta(hours=5):
                thread = info["thread"]
                await thread.send("This thread has been inactive for 5 hours and will be deleted.")
                await thread.delete()
                to_delete.append(user_id)

        for user_id in to_delete:
            del self.active_threads[user_id]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for user_id, info in self.active_threads.items():
            if info["thread"].id == message.channel.id:
                info["last_activity"] = datetime.utcnow()

async def setup(bot):
    await bot.add_cog(MeetAFriend(bot))
