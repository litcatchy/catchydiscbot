import discord
from discord.ext import commands
import random
import re

class PP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile(r",pp\s*when\s*i\s*see\s*<@!?(\d+)>", re.IGNORECASE)
        self.sizes = [
            "8=>", "8==>", "8===>", "8====>", "8=====>", "8======>",
            "8=======>", "8========>", "8===========>", "8===============>",
            "8===================>", "8=========================>",
            "8=================================>", "8===================================================>",
            "8=========================================================================================================>"
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower().replace(" ", "")

        if content.startswith(",pp"):
            match = self.pattern.match(message.content.lower().replace(" ", ""))
            if match:
                user_id = int(match.group(1))
                target = message.guild.get_member(user_id)
                if target is None:
                    return
            else:
                target = message.author

            size = random.choice(self.sizes)
            embed = discord.Embed(description=size, color=discord.Color.purple())
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PP(bot))
