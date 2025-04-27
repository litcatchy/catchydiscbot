import discord
from discord.ext import commands
from datetime import datetime, timedelta
from discord.utils import utcnow

class Boosts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_recent_boosters(self, channel):
        # Get the current UTC time (timezone-aware)
        eighteen_days_ago = utcnow() - timedelta(days=18)
        
        recent_boosters = []
        async for msg in channel.history(limit=100):  # Increase limit if needed
            # Ensure the created_at timestamp is timezone-aware
            if msg.created_at >= eighteen_days_ago:
                # Add the user and the boost date to the list
                if msg.type == discord.MessageType.add_reaction:
                    if "boost" in msg.content.lower():
                        recent_boosters.append((msg.author.name, msg.created_at))
        
        # Sort by the most recent boosts first
        recent_boosters.sort(key=lambda x: x[1], reverse=True)
        return recent_boosters[:5]  # Get top 5 recent boosters

    async def send_top_boosters(self, channel):
        boosters = await self.fetch_recent_boosters(channel)
        top_boosters_message = "Top 5 recent boosters:\n"
        
        for i, (name, _) in enumerate(boosters, 1):
            top_boosters_message += f"{i}. {name} x{boosters.count(name)} boost(s)\n"

        await channel.send(top_boosters_message)

    @commands.command(name='rb')
    async def recent_boosters(self, ctx):
        channel = ctx.guild.get_channel(1349127678694920202)  # Replace with your actual channel ID
        await self.send_top_boosters(channel)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if a user boosted
        if after.premium_since != before.premium_since and after.premium_since is not None:
            channel = self.bot.get_channel(1349127678694920202)  # Channel where boost thank you message will be sent
            thank_you_embed = discord.Embed(description=f"<@{after.id}> thank you so much for boosting bby! We love you so much. <:000:1358756048982249574>\n\n-# perks included: hoisted role, cute icon & image perms!", color=discord.Color.greyple())
            await channel.send(embed=thank_you_embed)
            await self.send_top_boosters(channel)

# Remove this function from here; it's unnecessary
# async def setup(bot):
#     bot.add_cog(Boosts(bot))

# Instead, modify the cog to add itself during startup
async def setup(bot):
    await bot.add_cog(Boosts(bot))
