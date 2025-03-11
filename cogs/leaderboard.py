import discord
from discord.ext import commands
import asyncio
from database import Database

db = Database()

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_timestamps = {}  # Stores last message time for each user to prevent spam

    async def send_embed(self, ctx, description, color=discord.Color.blue()):
        """Helper function to send an embed."""
        embed = discord.Embed(description=f"<:currencypaw:1346100210899619901> {description}", color=color)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Tracks messages and prevents spam counting."""
        if message.author.bot or message.guild is None:
            return
        
        user_id = message.author.id
        guild_id = message.guild.id
        current_time = asyncio.get_event_loop().time()

        last_time = self.message_timestamps.get(user_id, 0)
        if current_time - last_time >= 4:  # Prevents spam messages from being counted
            db.add_message(user_id, guild_id)
            self.message_timestamps[user_id] = current_time
        else:
            warning = await message.channel.send(f"<@{user_id}>, stop spamming! Messages count every 4 seconds.")
            await asyncio.sleep(5)
            await warning.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Tracks voice channel time."""
        if before.channel is None and after.channel is not None:  # User joins VC
            db.start_vc_timer(member.id, member.guild.id)
        elif before.channel is not None and after.channel is None:  # User leaves VC
            db.stop_vc_timer(member.id, member.guild.id)

    @commands.command(name="lb")
    async def user_stats(self, ctx, member: discord.Member = None):
        """Shows total messages sent & VC time spent by a user."""
        member = member or ctx.author
        total_messages = db.get_message_count(member.id, ctx.guild.id)
        vc_time = db.get_vc_time(member.id, ctx.guild.id)

        hours, remainder = divmod(vc_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"Stats for {member.name}", icon_url=member.avatar.url if member.avatar else None)
        embed.add_field(name="Total Messages", value=f"`{total_messages}`", inline=True)
        embed.add_field(name="Total VC Time", value=f"`{int(hours)}h {int(minutes)}m {int(seconds)}s`", inline=True)
        embed.set_footer(text="Leaderboard System | Crest Server")

        await ctx.send(embed=embed)

    @commands.command(name="topchat")
    async def top_chat(self, ctx):
        """Displays top message senders with pagination."""
        top_users = db.get_top_chat_users(ctx.guild.id, limit=10)
        if not top_users:
            return await self.send_embed(ctx, "No data available.")

        pages = [top_users[i:i + 10] for i in range(0, len(top_users), 10)]
        current_page = 0

        async def update_message():
            embed = discord.Embed(title="📊 Top Chatters", color=discord.Color.blue())
            for index, (user_id, message_count) in enumerate(pages[current_page], start=current_page * 10 + 1):
                embed.add_field(name=f"#{index} <@{user_id}>", value=f"`{message_count} messages`", inline=False)
            embed.set_footer(text=f"Page {current_page+1}/{len(pages)}")
            return embed

        message = await ctx.send(embed=await update_message())

        async def button_action(interaction, increment):
            nonlocal current_page
            if interaction.user != ctx.author:
                return await interaction.response.send_message("You cannot control this leaderboard!", ephemeral=True)

            current_page += increment
            current_page = max(0, min(current_page, len(pages) - 1))
            await message.edit(embed=await update_message())
            await interaction.response.defer()

        view = discord.ui.View()
        if len(pages) > 1:
            view.add_item(discord.ui.Button(label="⬅ Previous", style=discord.ButtonStyle.gray, custom_id="prev"))
            view.add_item(discord.ui.Button(label="➡ Next", style=discord.ButtonStyle.gray, custom_id="next"))

            async def button_callback(interaction):
                if interaction.custom_id == "prev":
                    await button_action(interaction, -1)
                elif interaction.custom_id == "next":
                    await button_action(interaction, 1)

            for item in view.children:
                item.callback = button_callback

        await message.edit(view=view)

    @commands.command(name="topvc")
    async def top_vc(self, ctx):
        """Displays top VC users with pagination."""
        top_users = db.get_top_vc_users(ctx.guild.id, limit=10)
        if not top_users:
            return await self.send_embed(ctx, "No data available.")

        pages = [top_users[i:i + 10] for i in range(0, len(top_users), 10)]
        current_page = 0

        async def update_message():
            embed = discord.Embed(title="🎙️ Top VC Users", color=discord.Color.blue())
            for index, (user_id, vc_time) in enumerate(pages[current_page], start=current_page * 10 + 1):
                hours, remainder = divmod(vc_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                embed.add_field(name=f"#{index} <@{user_id}>", value=f"`{int(hours)}h {int(minutes)}m {int(seconds)}s`", inline=False)
            embed.set_footer(text=f"Page {current_page+1}/{len(pages)}")
            return embed

        message = await ctx.send(embed=await update_message())

        async def button_action(interaction, increment):
            nonlocal current_page
            if interaction.user != ctx.author:
                return await interaction.response.send_message("You cannot control this leaderboard!", ephemeral=True)

            current_page += increment
            current_page = max(0, min(current_page, len(pages) - 1))
            await message.edit(embed=await update_message())
            await interaction.response.defer()

        view = discord.ui.View()
        if len(pages) > 1:
            view.add_item(discord.ui.Button(label="⬅ Previous", style=discord.ButtonStyle.gray, custom_id="prev"))
            view.add_item(discord.ui.Button(label="➡ Next", style=discord.ButtonStyle.gray, custom_id="next"))

            async def button_callback(interaction):
                if interaction.custom_id == "prev":
                    await button_action(interaction, -1)
                elif interaction.custom_id == "next":
                    await button_action(interaction, 1)

            for item in view.children:
                item.callback = button_callback

        await message.edit(view=view)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
