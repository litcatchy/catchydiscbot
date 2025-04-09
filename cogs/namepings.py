import discord
from discord.ext import commands
import random
import asyncio

class NamePing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name_map = {
            230022649844203522: ["catchy", "james"],
            1312006027197153318: ["wes", "wessie", "weasel"],
            691421268691648523: ["musk", "nm22", "nm"],
            1310705085797367851: ["cam", "cameron", "cami", "cams"],
            962581886318825483: ["yuki", "yukinon"],
            1339954295478419456: ["rey", "reyna"],
        }
        self.responses = [
            "Uh oh, someone's talking about {mention}!",
            "Did someone just say {mention}? I'm watching!",
            "{mention}, you just got name-dropped!",
            "Yoo {mention}, they talking about you!",
            "Guess who got mentioned? {mention}!",
            "Spotted {mention} in the wild!",
            "Careful, you're summoning {mention}!",
            "{mention}, your ears burning?",
            "Looks like {mention} is famous today!",
            "Alert! {mention} mentioned!"
        ]
        self.cooldown = {}  # channel_id: timestamp

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        current_time = asyncio.get_event_loop().time()
        last_trigger = self.cooldown.get(message.channel.id, 0)

        if current_time - last_trigger < 10:
            return  # Cooldown active

        content = message.content.lower()
        mentions = set()

        for user_id, keywords in self.name_map.items():
            for keyword in keywords:
                if keyword in content:
                    mentions.add(user_id)

        mentions.discard(message.author.id)

        if mentions:
            self.cooldown[message.channel.id] = current_time
            for user_id in mentions:
                mention = f"<@{user_id}>"
                response = random.choice(self.responses).format(mention=mention)
                await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(NamePing(bot))
