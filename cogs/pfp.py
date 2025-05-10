import discord
from discord.ext import commands, tasks
import random
import aiohttp
from bs4 import BeautifulSoup

class PFPDrop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1362801674560737462
        self.search_queries = [
            "egirl pfp site:pinterest.com",
            "anime aesthetic pfp site:pinterest.com",
            "dark anime girl pfp site:pinterest.com",
            "emo aesthetic pfp site:pinterest.com",
            "bloody aesthetic girl pfp site:pinterest.com",
            "money aesthetic pfp site:pinterest.com",
            "cat girl pfp anime site:pinterest.com",
        ]
        self.send_pfps.start()

    def cog_unload(self):
        self.send_pfps.cancel()

    @tasks.loop(minutes=5)
    async def send_pfps(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        query = random.choice(self.search_queries)
        image_urls = await self.fetch_images(query)

        if image_urls:
            for url in random.sample(image_urls, min(5, len(image_urls))):
                await channel.send(url)

    @send_pfps.before_loop
    async def before_pfps(self):
        await self.bot.wait_until_ready()

    async def fetch_images(self, query):
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}&form=HDRSC2"

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                image_elements = soup.select("a.iusc")
                
                results = []
                for tag in image_elements:
                    m = tag.get("m")
                    if m and '"murl":"' in m:
                        start = m.find('"murl":"') + len('"murl":"')
                        end = m.find('"', start)
                        image_url = m[start:end].replace("\\", "")
                        if any(ext in image_url for ext in [".jpg", ".jpeg", ".png"]):
                            results.append(image_url)
                return results

async def setup(bot):
    await bot.add_cog(PFPDrop(bot))
