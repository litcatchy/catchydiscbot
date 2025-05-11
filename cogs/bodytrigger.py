import discord
from discord.ext import commands
import aiohttp
import re
import asyncio
import random
from bs4 import BeautifulSoup

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Define the triggers and search queries
        self.triggers = {
            r"\blips?\b": ["aesthetic female lips site:pinterest.com"],
            r"\beyes?\b": ["aesthetic female eyes site:pinterest.com"],
            r"\bboobs?\b": ["boobs aesthetic site:pinterest.com", "aesthetic boobs site:pinterest.com"],
            r"\bwaists?\b": ["women aesthetic waist site:pinterest.com", "sexy women waist site:pinterest.com"],
            r"\babs?\b": ["female aesthetic abs site:pinterest.com", "male aesthetic abs site:pinterest.com"],
            r"\bass(?:es)?\b": ["female aesthetic ass site:pinterest.com", "sexy anime ass site:pinterest.com"],
            r"\bbiceps?\b": ["male aesthetic veiny biceps site:pinterest.com", "aesthetic biceps site:pinterest.com"],
            r"\bveins?\b": ["veiny arms aesthetic site:pinterest.com", "aesthetic veiny arms site:pinterest.com"],
            r"\bhunter eyes?\b": ["male aesthetic hunter eyes site:pinterest.com"],
            r"\bhands?\b": ["female aesthetic hands site:pinterest.com"],
            r"\bchoke\b": ["aesthetic choke site:pinterest.com", "aesthetic female getting choker site:pinterest.com"],
            r"\bbaths?\b|\bbathe?\b": ["aesthetic girl bath site:pinterest.com", "sexy anime bath site:pinterest.com"]
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for pattern, queries in self.triggers.items():
            if re.search(pattern, message.content, re.IGNORECASE):
                query = random.choice(queries)  # Randomly pick one search query
                img_url = await self.fetch_image(query)
                if img_url:
                    sent_msg = await message.channel.send(img_url)
                    await asyncio.sleep(3.5)  # Wait before deleting the image
                    await sent_msg.delete()
                break  # Exit the loop after the first match

        # Ensure the bot can still process commands after triggering
        await self.bot.process_commands(message)

    async def fetch_image(self, query):
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}&form=HDRSC2"

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    return None
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                image_elements = soup.select("a.iusc")
                random.shuffle(image_elements)  # Shuffle to avoid repetitive images
                for tag in image_elements:
                    m = tag.get("m")
                    if m and '"murl":"' in m:
                        start = m.find('"murl":"') + len('"murl":"')
                        end = m.find('"', start)
                        image_url = m[start:end].replace("\\", "")
                        if "pinterest" in image_url and any(ext in image_url for ext in [".jpg", ".jpeg", ".png"]):
                            return image_url
        return None

async def setup(bot):
    await bot.add_cog(PFPTrigger(bot))
