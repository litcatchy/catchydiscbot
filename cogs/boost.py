import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Boosts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_member_update(self, before, after):
        # Check if the user boosted
        if before.premium_since != after.premium_since:
            if after.premium_since:  # If the user just boosted
                channel = after.guild.get_channel(1349127678694920202)
                # Thank you embed message
                embed = discord.Embed(
                    description=f"<@{after.id}> thank you so much for boosting bby! we love you so much. <:000:1358756048982249574>\n\n-# perks included: hoisted role, cute icon & image perms!",
                    color=discord.Color.gray()
                )
                await channel.send(embed=embed)
                # Send the top 5 recent boosters message
                await self.send_top_boosters(channel)

    @commands.command()
    async def rb(self, ctx):
        # Command to show recent boosters
        channel = ctx.channel
        await self.send_top_boosters(channel)

    async def send_top_boosters(self, channel):
        # Fetch recent boost messages and top boosters
        boosters = await self.fetch_recent_boosters(channel)

        # Send the top boosters message
        top_boosters_embed = discord.Embed(
            title="Top 5 Recent Boosters",
            color=discord.Color.blue()
        )

        if boosters:
            for i, booster in enumerate(boosters[:5]):
                top_boosters_embed.add_field(name=f"{i+1}. {booster['name']}", value=f"x{booster['boosts']} boost", inline=False)
            await channel.send(embed=top_boosters_embed)
        else:
            await channel.send("No recent boosters found within the last 18 days.")

    async def fetch_recent_boosters(self, channel):
        eighteen_days_ago = datetime.now() - timedelta(days=18)
        boosters = []

        # Go through the messages in the channel to detect boosts
        async for msg in channel.history(limit=100):
            if msg.author.premium_since:  # Check if the user boosted
                if msg.created_at > eighteen_days_ago:
                    user = msg.author
                    # Count the number of boosts by this user
                    boost_count = sum(1 for m in await channel.history(limit=100).flatten() if m.author == user and m.author.premium_since)
                    boosters.append({'name': user.name, 'boosts': boost_count})

        return boosters


async def setup(bot):
    await bot.add_cog(Boosts(bot))  # Ensure add_cog() is awaited correctly
