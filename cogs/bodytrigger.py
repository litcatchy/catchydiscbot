import discord
from discord.ext import commands
import random
import re

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Define the triggers and Discord image links for each keyword
        self.triggers = {
            r"\blips?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_1}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_2}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_3}.jpg",
            ],
            r"\beyes?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_4}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_5}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_6}.jpg",
            ],
            r"\bboobs?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371136182003568791/9f6689276a87c4b62783606df6d75445.jpg?ex=68220994&is=6820b814&hm=049116be1164956b958e3bf7b393bb7d524a5a0ffa9ccc5d7dc422d64d040c72&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371136745910829117/18284919a184ef1b592b2ae9a3d22684.jpg?ex=68220a1a&is=6820b89a&hm=e88707bf06248d343d6af3a67a3975bb1396f4d1577a886ca487d9f67bc0ebd3&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371136761400529046/658cbff7b64550ad5c9c9a2d2f22c671.jpg?ex=68220a1e&is=6820b89e&hm=442b8461f2ed2704ce4d80e87837dc5ec4115ba472a18bb3e5426e3d0433661a&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371137298795724800/9bd728af589af668f150ab9f037b90cf.jpg?ex=68220a9e&is=6820b91e&hm=78ceb30b90305381ef248ae3378c54df5273ae3e9d24a9365a3a638c7d172e35&",
            ],
            r"\bwaists?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_11}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_12}.jpg",
            ],
            r"\babs?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_13}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_14}.jpg",
            ],
            r"\bass(es)?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_15}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_16}.jpg",
            ],
            r"\bbiceps?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_17}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_18}.jpg",
            ],
            r"\bveins?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_19}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_20}.jpg",
            ],
            r"\bhunter eyes?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_21}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_22}.jpg",
            ],
            r"\bhands?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_23}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_24}.jpg",
            ],
            r"\bchoke\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_25}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_26}.jpg",
            ],
            r"\bbaths?\b|\bbathe?\b": [
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_27}.jpg",
                "https://cdn.discordapp.com/attachments/{channel_id}/{image_id_28}.jpg",
            ]
        }
        
        # Dictionary to track images sent for each keyword
        self.sent_images = {keyword: [] for keyword in self.triggers}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for pattern, urls in self.triggers.items():
            if re.search(pattern, message.content, re.IGNORECASE):
                # Filter out the URLs that have already been sent
                available_urls = [url for url in urls if url not in self.sent_images[pattern]]
                
                if not available_urls:
                    # If all images have been sent, reset the list of sent images for this keyword
                    self.sent_images[pattern] = []
                    available_urls = urls
                
                # Select a random image from the available URLs
                image_url = random.choice(available_urls)
                
                # Mark the selected image as sent
                self.sent_images[pattern].append(image_url)
                
                # Send the image URL as an image in Discord
                await message.channel.send(image_url)
                break

async def setup(bot):
    await bot.add_cog(PFPTrigger(bot))
