import discord
from discord.ext import commands
import re
import random

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.triggers = {
            r"\blips?\b": [
                "https://cdn.discordapp.com/attachments/123456/lips1.png",
                "https://cdn.discordapp.com/attachments/123456/lips2.png",
                "https://cdn.discordapp.com/attachments/123456/lips3.png",
            ],
            r"\beyes?\b": [
                "https://cdn.discordapp.com/attachments/123456/eyes1.png",
                "https://cdn.discordapp.com/attachments/123456/eyes2.png",
                "https://cdn.discordapp.com/attachments/123456/eyes3.png",
            ],
            r"\bboobs?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371136182003568791/9f6689276a87c4b62783606df6d75445.jpg?ex=68220994&is=6820b814&hm=049116be1164956b958e3bf7b393bb7d524a5a0ffa9ccc5d7dc422d64d040c72&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371137298795724800/9bd728af589af668f150ab9f037b90cf.jpg?ex=68220a9e&is=6820b91e&hm=78ceb30b90305381ef248ae3378c54df5273ae3e9d24a9365a3a638c7d172e35&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371139160144089178/fcc9f273fcc62b217efb69cad994c9d5.jpg?ex=68220c5a&is=6820bada&hm=1ec36f42e85325f74eb90a959d32d68b8e9615493ec684c580989c393ae9e695&",
            ],
            r"\bwaists?\b": [
                "https://cdn.discordapp.com/attachments/123456/waist1.png",
                "https://cdn.discordapp.com/attachments/123456/waist2.png",
                "https://cdn.discordapp.com/attachments/123456/waist3.png",
            ],
            r"\babs?\b": [
                "https://cdn.discordapp.com/attachments/123456/abs1.png",
                "https://cdn.discordapp.com/attachments/123456/abs2.png",
                "https://cdn.discordapp.com/attachments/123456/abs3.png",
            ],
            r"\bass(es)?\b": [
                "https://cdn.discordapp.com/attachments/123456/ass1.png",
                "https://cdn.discordapp.com/attachments/123456/ass2.png",
                "https://cdn.discordapp.com/attachments/123456/ass3.png",
            ],
            r"\bbiceps?\b": [
                "https://cdn.discordapp.com/attachments/123456/biceps1.png",
                "https://cdn.discordapp.com/attachments/123456/biceps2.png",
                "https://cdn.discordapp.com/attachments/123456/biceps3.png",
            ],
            r"\bveins?\b": [
                "https://cdn.discordapp.com/attachments/123456/veins1.png",
                "https://cdn.discordapp.com/attachments/123456/veins2.png",
                "https://cdn.discordapp.com/attachments/123456/veins3.png",
            ],
            r"\bhunter eyes?\b": [
                "https://cdn.discordapp.com/attachments/123456/hunter1.png",
                "https://cdn.discordapp.com/attachments/123456/hunter2.png",
                "https://cdn.discordapp.com/attachments/123456/hunter3.png",
            ],
            r"\bhands?\b": [
                "https://cdn.discordapp.com/attachments/123456/hands1.png",
                "https://cdn.discordapp.com/attachments/123456/hands2.png",
                "https://cdn.discordapp.com/attachments/123456/hands3.png",
            ],
            r"\bchoke\b": [
                "https://cdn.discordapp.com/attachments/123456/choke1.png",
                "https://cdn.discordapp.com/attachments/123456/choke2.png",
                "https://cdn.discordapp.com/attachments/123456/choke3.png",
            ],
            r"\bbaths?\b|\bbathe?\b": [
                "https://cdn.discordapp.com/attachments/123456/bath1.png",
                "https://cdn.discordapp.com/attachments/123456/bath2.png",
                "https://cdn.discordapp.com/attachments/123456/bath3.png",
            ],
            r"\bfeet\b": [
                "https://cdn.discordapp.com/attachments/123456/feet1.png",
                "https://cdn.discordapp.com/attachments/123456/feet2.png",
                "https://cdn.discordapp.com/attachments/123456/feet3.png",
            ]
        }

        self.sent_images = {pattern: [] for pattern in self.triggers}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for pattern, urls in self.triggers.items():
            if re.search(pattern, message.content, re.IGNORECASE):
                available = [u for u in urls if u not in self.sent_images[pattern]]

                if not available:
                    self.sent_images[pattern] = []
                    available = urls

                selected = random.choice(available)
                self.sent_images[pattern].append(selected)

                await message.channel.send(selected, delete_after=3)
                break

async def setup(bot):
    await bot.add_cog(PFPTrigger(bot))
