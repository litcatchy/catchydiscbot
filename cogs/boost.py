
import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Boosts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Send the thank you embed when a user boosts
    async def send_thank_you_embed(self, channel, user):
        embed = discord.Embed(
            description=f"<@{user.id}> thank you so much for boosting bby! we love you so much. <:000:1358756048982249574>\n\n-# perks included: hoisted role, cute icon & image perms!",
            color=discord.Color.gray()
        )
        await channel.send(embed=embed)

    # Fetch the recent boosters (from the last 18 days)
    async def fetch_recent_boosters(self, channel):
        boosters = []
        eighteen_days_ago = datetime.utcnow() - timedelta(days=18)

        # Fetch the last 100 messages in the channel
        async for msg in channel.history(limit=100):
            if msg.type == discord.MessageType.premium_guild_subscription:  # Corrected here
                # Check if the message is within the last 18 days
                if msg.created_at > eighteen_days_ago:
                    boosters.append(msg.author)

        return boosters

    # Send the top 5 recent boosters
    async def send_top_boosters(self, channel):
        boosters = await self.fetch_recent_boosters(channel)
        boosters = list(set(boosters))  # Remove duplicates

        # Sort the boosters based on how recent their boost is
        boosters.sort(key=lambda x: x.joined_at, reverse=True)

        # Generate the message for top boosters
        top_boosters_message = "Top 5 recent boosters:\n"
        for i, booster in enumerate(boosters[:5]):
            # Count how many times each booster has boosted
            boost_count = boosters.count(booster)
            top_boosters_message += f"{i+1}. {booster.name} x{boost_count} boost{'s' if boost_count > 1 else ''}\n"

        await channel.send(top_boosters_message)

    # Command to handle boost notifications and show the recent boosters
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if the member boosted the server
        if before.premium_since is None and after.premium_since is not None:
            boost_channel = self.bot.get_channel(1349127678694920202)  # Your channel for boost messages
            thank_you_channel = self.bot.get_channel(1349127678694920202)  # Same or different channel for thank you message

            # Send thank you message
            await self.send_thank_you_embed(thank_you_channel, after)

            # Send top 5 boosters message
            await self.send_top_boosters(boost_channel)

    # Command to check the recent boosters manually
    @commands.command(name='rb')
    async def recent_boosters(self, ctx):
        # Only allow this command in specific channels
        if ctx.channel.id != 1349127678694920202:
            return

        await self.send_top_boosters(ctx.channel)

def setup(bot):
    bot.add_cog(Boosts(bot))
