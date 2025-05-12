import discord
from discord.ext import commands
import random

class Insult(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.insults = [
            "Have a nice day… somewhere else.",
            "I’d love to keep chatting with you, but I’d rather have AIDS.",
            "Unless your name is Google, stop acting like you know everything.",
            "You bring everyone so much joy… when you leave the room.",
            "You have something on your chin… no, the third one down.",
            "Your secrets are always safe with me. I never even listen.",
            "You are the reason shampoo has instructions.",
            "If I had your looks, I’d sue my parents.",
            "You're not “him” you're “who invited him.”",
            "You have something money can’t buy… a really low IQ.",
            "You’re the reason autocorrect gives up.",
            "You bring everyone so much happiness… when you log off.",
            "If I had a dollar for every smart thing you said, I’d be broke.",
            "I’d roast you but nature already did.",
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "You got zero rizz and negative IQ.",
            "I’d agree with you, but then we’d both be wrong.",
            "You have something most people don’t. A complete lack of self-awareness.",
            "You're the reason Discord has a block button.",
            "You're like a software update. Takes forever and changes nothing.",
            "You're proof that evolution can go in reverse.",
            "Your parents had 9 months and still fumbled.",
            "You're what happens when the cousin-kissing gets too serious.",
            "You are about as helpful as a screen door on a submarine.",
            "You're not funny, you're just loud.",
            "You’ve got something on your lip… oh, it’s just your ego.",
            "Your parents had 9 months and still fumbled.",
            "You're what happens when cousins marry.",
            "You're the reason shampoo bottles say “do not drink.”",
            "You're the reason Discord servers have mute buttons.",
            "If cringe was a currency, you'd be a millionaire.",
            "Even your imaginary friend ghosted you.",
            "You bring the average IQ down by just showing up.",
            "You look like the reason group projects fail.",
            "You must be the human version of a software bug.",
            "You look like the reason group projects fail.",
            "You’re a few fries short of a Happy Meal.",
            "You look like your parents met on Omegle.",
            "You’re like a broken pencil—pointless.",
            "You're the reason Discord servers have mute buttons.",
            "Your personality is like a dial-up connection. Painful and outdated.",
            "Your idea of multitasking is screwing up more than one thing at once.",
            "You make sloths look productive.",
            "You’re the opposite of inspirational.",
            "You’re the kind of person people warn their friends about.",
            "Your thoughts have the depth of a kiddie pool.",
            "Your opinion is almost as unwanted as your presence.",
            "You’ve reached the peak of mediocrity.",
            "You’ve got a face for radio and a voice for silent films.",
            "You add nothing to conversations except awkward pauses.",
            "You're the reason Discord servers have mute buttons.",
            "Your face makes onions cry in defense.",
            "You’re like a low-resolution meme—blurry and irrelevant.",
        ]

    @commands.command(name="insult")
    async def insult(self, ctx):
        if not ctx.message.mentions:
            embed = discord.Embed(
                description="Mentioning someone to insult is a required argument.",
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed)
            return

        target = ctx.message.mentions[0]
        author = ctx.author

        embed = discord.Embed(
            title=f"{author.mention} insulted {target.mention}",
            description=random.choice(self.insults),
            color=discord.Color.purple()
        )
        embed.set_footer(text="Boom, roasted!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Insult(bot))
