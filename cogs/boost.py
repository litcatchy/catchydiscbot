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
        # Mention the user who boosted and thank them
        user = ctx.author
        await self.send_thank_you_message(user, channel)
        # Send the top boosters message after thanking
        await self.send_top_boosters(channel)

    async def send_thank_you_message(self, user, channel):
        """Sends a thank you message to the user who boosted."""
        thank_you_embed = discord.Embed(
            title="Thank You for Boosting!",
            description=f"<@{user.id}> thank you so much for boosting bby! We love you so much. <:000:1358756048982249574>\n\n"
                        f"-# Perks included: hoisted role, cute icon & image perms!",
            color=discord.Color.greyple()  # Grey color for the embed
        )
        await channel.send(embed=thank_you_embed)

    async def send_top_boosters(self, channel):
        """Sends the top boosters to the channel."""
        boosters = await self.fetch_recent_boosters(channel)
        
        if not boosters:
            embed = discord.Embed(
                title="No Boosters Found",
                description="No boosters found in the last 14 days.",
                color=discord.Color.greyple()  # Grey color for the embed
            )
            await channel.send(embed=embed)
            return

        # Sort boosters by the number of boosts (assuming boosters is a list of users)
        sorted_boosters = sorted(boosters, key=lambda user: user['boost_count'], reverse=True)
        
        # Prepare the message to send top boosters in embed
        embed = discord.Embed(
            title="Top Boosters in the Last 14 Days",
            description="Here are the top boosters in the last 14 days:",
            color=discord.Color.greyple()  # Grey color for the embed
        )
        
        for index, booster in enumerate(sorted_boosters[:5], start=1):
            embed.add_field(
                name=f"{index}. {booster['user'].name}",
                value=f"Boosts: {booster['boost_count']}",
                inline=False
            )
        
        await channel.send(embed=embed)

    async def fetch_recent_boosters(self, channel):
        """Fetches the users who boosted in the last 14 days."""
        boosters = []
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        fourteen_days_ago = now - datetime.timedelta(days=14)

        # Iterate through the message history
        async for msg in channel.history(limit=100):
            # Only consider messages from the last 14 days
            if msg.created_at > fourteen_days_ago:
                # Check if the user has boosted the server (i.e., is a member with premium_since attribute)
                if isinstance(msg.author, discord.Member) and msg.author.premium_since:
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
