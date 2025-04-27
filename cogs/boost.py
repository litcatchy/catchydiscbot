import discord
from discord.ext import commands

class BoostTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.booster_channel_id = 1349127678694920202  # your boost channel ID

    @commands.command()
    async def boost(self, ctx):
        if ctx.channel.id != self.booster_channel_id:
            return await ctx.send("Use this command in the boost channel.")

        boosters = await self.fetch_recent_boosters(ctx.channel)

        if boosters:
            booster_text = ""
            for idx, (user_name, boost_count) in enumerate(boosters, start=1):
                booster_text += f"{idx}. {user_name} x{boost_count} boost\n"
        else:
            booster_text = "No boosters yet."

        embed = discord.Embed(
            description=f"**Top 5 recent boosters:**\n{booster_text}",
            color=discord.Color.greyple()
        )
        await ctx.send(embed=embed)

    async def fetch_recent_boosters(self, channel):
        boosters = {}

        async for message in channel.history(limit=200):
            if message.type == discord.MessageType.premium_guild_subscription:
                user = message.author
                if user:
                    boosters[user.name] = boosters.get(user.name, 0) + 1

        sorted_boosters = sorted(boosters.items(), key=lambda x: -x[1])
        return sorted_boosters[:5]  # Only top 5

async def setup(bot):
    await bot.add_cog(BoostTest(bot))
