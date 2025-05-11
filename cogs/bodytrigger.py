import discord
from discord.ext import commands
import re
import asyncio
import random

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Define the triggers and Pinterest links for each keyword
        self.triggers = {
            r"\blips?\b": [
                "https://pin.it/7tv21e6Pj",
                "https://pin.it/7tv3L7XeF"
            ],
            r"\beyes?\b": [
                "https://pin.it/4QksXfb",
                "https://pin.it/7ztnz4BQ"
            ],
            r"\bboobs?\b": [
                "https://pin.it/3dvGvlQZ0",
                "https://pin.it/7u9Tsqv6A",
                "https://pin.it/4ew5Yj4JE",
                "https://pin.it/1MHt4JE5v",
                "https://pin.it/4WcD8sMLz",
                "https://pin.it/2FhJUbe4K",
                "https://pin.it/6f0poPxHX",
                "https://pin.it/1agwsl8s1",
                "https://pin.it/1RifvFxEE",
                "https://pin.it/7480nBNfw",
                "https://pin.it/tvjCniP5f",
                "https://pin.it/5m6lllUOu",
                "https://pin.it/2lN4oujF9",
                "https://pin.it/4vLABamvx",
                "https://pin.it/4jSBhKxtQ",
                "https://pin.it/41U5QbEzi",
                "https://pin.it/5bwHeU0oi",
                "https://pin.it/2wZ417Afg",
                "https://pin.it/3RzXo9nwy",
                "https://pin.it/vmnqEpkHi",
                "https://pin.it/4mNscom13",
                "https://pin.it/2pRSGVypb",
                "https://pin.it/5bnjaUdjI",
                "https://pin.it/76Hmgsgqy",
                "https://pin.it/7w4t2ndAi",
                "https://pin.it/6z8xPrsnE",
                "https://pin.it/3Fx68L0fe",
            ],
            r"\bwaists?\b": [
                "https://pin.it/3hmmovN",
                "https://pin.it/7SHgK1f"
            ],
            r"\babs?\b": [
                "https://pin.it/3Qk0h82",
                "https://pin.it/2Vw5cXr"
            ],
            r"\bass(es)?\b": [
                "https://pin.it/2kGdrK4",
                "https://pin.it/7mGLZ69"
            ],
            r"\bbiceps?\b": [
                "https://pin.it/7yJwxaR",
                "https://pin.it/4onHn70"
            ],
            r"\bveins?\b": [
                "https://pin.it/4r4Lg1X",
                "https://pin.it/5HpqkZK"
            ],
            r"\bhunter eyes?\b": [
                "https://pin.it/7ALc6J8",
                "https://pin.it/6EkMkKP"
            ],
            r"\bhands?\b": [
                "https://pin.it/4vj7VJm",
                "https://pin.it/7rhD6pz"
            ],
            r"\bchoke\b": [
                "https://pin.it/7UNz0Mj",
                "https://pin.it/6TYlTzE"
            ],
            r"\bbaths?\b|\bbathe?\b": [
                "https://pin.it/6gZ9i2L0",
                "https://pin.it/2tL7o8Y8"
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
