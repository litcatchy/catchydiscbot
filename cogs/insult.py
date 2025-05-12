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
            "You have something on your lip. Oh wait, it's your entire personality.",
            "You have something money can’t buy… a really low IQ.",
            "You’re the reason autocorrect gives up.",
            "You bring everyone so much happiness… when you log off.",
            "If I had a dollar for every smart thing you said, I’d be broke.",
            "Your voice is like a lullaby. I fall asleep from boredom.",
            "I’d roast you but nature already did.",
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "You got zero rizz and negative IQ.",
            "I’d agree with you, but then we’d both be wrong.",
            "You have something most people don’t. A complete lack of self-awareness.",
            "You’re not the sharpest knife in the drawer. Or the cleanest.",
            "You're like a software update. Takes forever and changes nothing.",
            "You're proof that evolution can go in reverse.",
            "You’re as sharp as a marble.",
            "You’re the kind of person who claps when the plane lands.",
            "You're a gray sprinkle on a rainbow cupcake.",
            "You're the human version of a participation trophy.",
            "You're what happens when the cousin-kissing gets too serious.",
            "You are about as helpful as a screen door on a submarine.",
            "You're the reason we have warning labels on everything.",
            "You’ve got something on your lip… oh, it’s just your ego.",
            "You’re like a puzzle with half the pieces missing.",
            "You're what happens when cousins marry.",
            "You're the reason shampoo bottles say “do not drink.”",
            "You have the energy of a dead plant.",
            "You have something going for you. I’m just not sure what it is.",
            "You should wear a sign that says ‘doesn’t play well with others’.",
            "You bring the average IQ down by just showing up.",
            "You’re the emoji version of a typo.",
            "You must be the human version of a software bug.",
            "You’re like Wi-Fi—weak and inconsistent.",
            "You’re a few fries short of a Happy Meal.",
            "You’d struggle to pour water out of a boot if the instructions were on the heel.",
            "You’re like a broken pencil—pointless.",
            "You bring people together—just to talk about you.",
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
            "You’re not ugly, but you sure are trying.",
            "You’re not the worst… but you’re in the top 5.",
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
