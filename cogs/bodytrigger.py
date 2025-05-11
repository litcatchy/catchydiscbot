import discord
from discord.ext import commands
import aiohttp
import re
import asyncio
from bs4 import BeautifulSoup

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.triggers = {
            r"\blips?\b": "aesthetic female lips",
            r"\beyes?\b": "aesthetic female eyes",
            r"\bboobs?\b": "boobs aesthetic",
            r"\bwaists?\b": "women aesthetic waist",
            r"\babs?\b": "female aesthetic abs",
            r"\bass(es)?\b": "female aesthetic ass",
            r"\bbiceps?\b": "male aesthetic veiny biceps",
            r"\bveins?\b": "veiny arms aesthetic",
            r"\bhunter eyes?\b": "male aesthetic hunter eyes",
            r"\bhands?\b": "female aesthetic hands",
            r"\bchoke\b": "aesthetic choke",
            r"\bbathe?\b": "aesthetic girl bath",
            r"\bbaths?\b": "aesthetic girl bath"
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for pattern, query in self.triggers.items():
            if re.search(pattern, message.content, re.IGNORECASE):
                img_url = await self.fetch_image(query)
                if img_url:
                    sent_msg = await message.channel.send(img_url)
                    await asyncio.sleep(3.5)
                    await sent_msg.delete()
                break

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
    await bot.add_cog(PFPTrigger(bot))
