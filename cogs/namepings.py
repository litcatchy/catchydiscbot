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
            "{mention}, they’re talking about you.",
            "I heard someone mention {mention}.",
            "{mention}, your name just came up.",
            "{mention}, you might want to check this out.",
            "Looks like {mention} is in the conversation.",
            "Looks like {mention} is famous today.",
            "{mention}, you got mentioned.",
        ]
        self.special_responses = {
            962581886318825483: [  # Yuki
                "Hai {mention}, the slaves are calling you.",
            ],
            230022649844203522: [  # Catchy
                "Another day, another {mention} mention. ",
            ]
        }
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
            async with message.channel.typing():
                await asyncio.sleep(random.uniform(0.3, 1.0))  # slight typing delay

            for user_id in mentions:
                mention = f"<@{user_id}>"

                if user_id in self.special_responses:
                    response = random.choice(self.special_responses[user_id]).format(mention=mention)
                else:
                    response = random.choice(self.responses).format(mention=mention)

                await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(NamePing(bot))
