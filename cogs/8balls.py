import discord
from discord.ext import commands
import random
import re

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = [
            "My sources say yes.",
            "My sources say no.",
            "Wayy tOO B!G!",
            "Don’t tell anyone but of course.",
            "Never! :c",
            "Friend... nu.",
            "Yes b-baka.",
            "Only today, mom.",
            "Daddy... you get.",
            "As if!",
            "100% yes... maybe.",
            "Outlook not so good.",
            "Try again later.",
            "For sure, cutie.",
            "No. Just no.",
            "Stop with the boring questions.",
            "You’re not ready for that answer.",
            "Ask someone hotter.",
            "Ask again when you’re cooler.",
            "What do you think, dummy?",
            "In your dreams.",
            "Obviously.",
            "Hell yeah.",
            "Only if you say pretty please.",
            "I’m too tired to answer that.",
            "Lemme nap first...",
            "shutup ugly",
            "The universe says yes.",
            "I wouldn’t bet on it.",
            "That’s a secret~",
            "No thoughts, try again.",
            "Yes... but why tho?",
            "It’s complicated.",
            "You wish.",
            "Senpai noticed you, so yes.",
            "Nyaa~ maybe.",
            "No, but I still love you.",
            "Yes, with extra sparkles!",
            "The stars aligned for a yes.",
            "You’re too cringe to ask that.",
            "Only if you give me snacks.",
            "Meow~ try again.",
            "Ask again after 3 headpats.",
            "UwU what’s this? A yes.",
            "Nope. Try Alt+F4.",
            "Error 404: Answer not found.",
            "Too kawaii to respond"
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower().replace(" ", "")
        if content.startswith(("8ball", ",8ball", "8b", ",8b")):
            embed = discord.Embed(
                description=random.choice(self.responses),
                color=discord.Color.purple()
            )
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EightBall(bot))
