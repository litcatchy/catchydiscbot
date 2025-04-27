import discord
from discord.ext import commands
import datetime
import pytz

class Boosts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rb")
    async def rb(self, ctx):
        """Command to display the top boosters."""
        channel = ctx.channel
        await self.send_top_boosters(channel)

    async def send_top_boosters(self, channel):
        """Sends the top boosters to the channel."""
        boosters = await self.fetch_recent_boosters(channel)
        
        if not boosters:
            await channel.send("No boosters found in the last 14 days.")
            return

        # Sort boosters by the number of boosts (assuming boosters is a list of users)
        # You can add more complex sorting here if necessary
        sorted_boosters = sorted(boosters, key=lambda user: user['boost_count'], reverse=True)
        
        # Prepare the message to send top boosters
        message = "Top Boosters in the last 14 days:\n"
        for index, booster in enumerate(sorted_boosters[:5], start=1):
            message += f"{index}. {booster['user'].name} - Boosts: {booster['boost_count']}\n"
        
        await channel.send(message)

    async def fetch_recent_boosters(self, channel):
        """Fetches the users who boosted in the last 14 days."""
        boosters = []
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        fourteen_days_ago = now - datetime.timedelta(days=14)

        # Iterate through the message history
        async for msg in channel.history(limit=100):
            # Only consider messages from the last 14 days
            if msg.created_at > fourteen_days_ago:
                # Check if the user has boosted the server
                if msg.author.premium_since:
                    # Find if the user is already in the list, and if so, increment their boost count
                    existing_booster = next((b for b in boosters if b['user'] == msg.author), None)
                    if existing_booster:
                        existing_booster['boost_count'] += 1
                    else:
                        boosters.append({'user': msg.author, 'boost_count': 1})

        return boosters


# The setup function is required for loading the cog correctly in main.py
async def setup(bot):
    await bot.add_cog(Boosts(bot))
