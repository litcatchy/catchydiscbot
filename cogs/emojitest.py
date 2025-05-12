import discord
from discord.ext import commands

class EmojiTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def emojitest(self, ctx):
        coowner = "<:coowner:1371463627705421844>"
        admin = "<:admin:1371463646370201630>"
        staff = "<:staff:1371463638375993374>"

        embed = discord.Embed(color=discord.Color.purple())
        embed.description = f"{coowner} {admin} {staff}"
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EmojiTest(bot))
