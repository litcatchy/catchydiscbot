import discord
from discord.ext import commands
import datetime

class BoosterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.booster_channel_id = 1349127678694920202  # your boost channel ID

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.booster_channel_id:
            return

        if message.type == discord.MessageType.premium_guild_subscription:
            await self.handle_boost(message)

    async def handle_boost(self, message):
        # Thank you embed
        thank_you_embed = discord.Embed(
            description=f"{message.author.mention} thank you so much for boosting bby! we love you so much. <:000:1358756048982249574>\n\n"
                        "-# perks included: hoisted role, cute icon & image perms!",
            color=discord.Color.greyple()
        )
        await message.channel.send(embed=thank_you_embed)

        # After thank you, send Top 5 boosters
        await self.send_top_boosters(message.channel)

    async def fetch_recent_boosters(self, channel):
        boosters = {}

        now = datetime.datetime.utcnow()
        eighteen_days_ago = now - datetime.timedelta(days=18)

        async for msg in channel.history(limit=500):
            if msg.created_at < eighteen_days_ago:
                continue

            if msg.type == discord.MessageType.premium_guild_subscription:
                user = msg.author
                if user:
                    boosters[user.name] = boosters.get(user.name, 0) + 1

        sorted_boosters = sorted(boosters.items(), key=lambda x: -x[1])
        return sorted_boosters[:5]

    async def send_top_boosters(self, channel):
        boosters = await self.fetch_recent_boosters(channel)

        if boosters:
            booster_text = ""
            for idx, (user_name, boost_count) in enumerate(boosters, start=1):
                booster_text += f"{idx}. {user_name} x{boost_count} boost\n"
        else:
            booster_text = "No boosters yet."

        leaderboard_embed = discord.Embed(
            description=f"**Top 5 recent boosters:**\n{booster_text}",
            color=discord.Color.greyple()
        )
        await channel.send(embed=leaderboard_embed)

    @commands.command(name="rb")
    async def recent_boosters(self, ctx):
        if ctx.channel.id != self.booster_channel_id:
            return await ctx.send("This command can only be used in the boost channel.")

        await self.send_top_boosters(ctx.channel)

async def setup(bot):
    await bot.add_cog(BoosterCog(bot))
