import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re

class BodyTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_map = {
            "lips": "aesthetic female lips",
            "eyes": "aesthetic female eyes",
            "boobs": "aesthetic boobs",
            "waist": "sexy women waist",
            "abs": "female aesthetic abs",
            "ass": "female aesthetic ass",
            "biceps": "aesthetic biceps",
            "veins": "veiny arms aesthetic",
            "hunter eyes": "male aesthetic hunter eyes",
            "hands": "female aesthetic hands",
            "choke": "aesthetic female getting choked",
            "bath": "aesthetic girl bath",
            "bathe": "aesthetic girl bath"
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()
        for trigger, query in self.word_map.items():
            pattern = r'\b' + re.escape(trigger.rstrip("s")) + r's?\b'
            if re.search(pattern, content):
                image_url = await self.fetch_image(query)
                if image_url:
                    sent = await message.channel.send(image_url)
                    await asyncio.sleep(1.3)
                    try:
                        await sent.delete()
                    except discord.NotFound:
                        pass
                break

    async def fetch_image(self, query):
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}+site:pinterest.com"

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                image_elements = soup.select("a.iusc")

                for tag in image_elements:
                    m = tag.get("m")
                    if m and '"murl":"' in m:
                        start = m.find('"murl":"') + len('"murl":"')
                        end = m.find('"', start)
                        image_url = m[start:end].replace("\\", "")
                        if any(ext in image_url for ext in [".jpg", ".jpeg", ".png"]):
                            return image_url
        return None

async def setup(bot):
    await bot.add_cog(BodyTrigger(bot))
