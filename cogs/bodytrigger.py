import discord
from discord.ext import commands
import aiohttp
import re
import asyncio
from bs4 import BeautifulSoup

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sent_images = set()  # To keep track of already sent images
        
        self.triggers = {
            r"\blips?\b": ["aesthetic female lips", "female aesthetic lips"],
            r"\beyes?\b": ["aesthetic female eyes", "beautiful female eyes", "cute eyes aesthetic"],
            r"\bboobs?\b": ["boobs aesthetic", "aesthetic boobs", "sexy aesthetic boobs"],
            r"\bwaists?\b": ["women aesthetic waist", "sexy women waist", "aesthetic waistline"],
            r"\babs?\b": ["female aesthetic abs", "male aesthetic abs", "sexy abs aesthetic"],
            r"\bass(es)?\b": ["female aesthetic ass", "aesthetic buttocks", "curvy aesthetic ass", "sexy ass aesthetic"],
            r"\bbiceps?\b": ["male aesthetic veiny biceps", "aesthetic biceps", "biceps aesthetic"],
            r"\bveins?\b": ["veiny arms aesthetic", "aesthetic veiny arms", "veins aesthetic"],
            r"\bhunter eyes?\b": ["male aesthetic hunter eyes", "aesthetic hunter eyes"],
            r"\bhands?\b": ["female aesthetic hands", "aesthetic hands", "pretty hands aesthetic"],
            r"\bchoke\b": ["aesthetic choke", "aesthetic female getting choked"],
            r"\bbathe?\b": ["aesthetic girl bath", "beautiful girl bath", "sexy girl bath"],
            r"\bbaths?\b": ["aesthetic girl bath", "beautiful girl bath", "sexy girl bath"]
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for pattern, queries in self.triggers.items():
            if re.search(pattern, message.content, re.IGNORECASE):
                for query in queries:
                    img_url = await self.fetch_image(query)
                    if img_url and img_url not in self.sent_images:
                        sent_msg = await message.channel.send(img_url)
                        await asyncio.sleep(3.5)  # Wait for 3.5 seconds before deleting the message
                        await sent_msg.delete()
                        self.sent_images.add(img_url)
                        if len(self.sent_images) > 10:
                            self.sent_images.pop()  # Remove oldest image URL if more than 10 images are stored
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
