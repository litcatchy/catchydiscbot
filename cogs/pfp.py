import discord
from discord.ext import commands, tasks
import random
import aiohttp
from bs4 import BeautifulSoup
import asyncio

class PFPDrop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1362801674560737462  # Your channel ID
        self.search_queries = [
            "femboy anime aesthetic pfp site:pinterest.com",
            "goth girl aesthetic pfp site:pinterest.com",
            "dark romance aesthetic pfp site:pinterest.com",
            "aesthetic girl tied up pfp site:pinterest.com",
            "yandere anime girl pfp site:pinterest.com",
            "emo aesthetic anime pfp site:pinterest.com",
            "alt aesthetic anime pfp site:pinterest.com",
            "money aesthetic pfp site:pinterest.com",
            "crazy anime girl aesthetic pfp site:pinterest.com",
            "soft bloody cute anime pfp site:pinterest.com",
            "egirl aesthetic pfp discord site:pinterest.com",
            "eboy aesthetic pfp discord site:pinterest.com",
            "cat girl pfp site:pinterest.com"
        ]
        self.send_pfps.start()

    def cog_unload(self):
        self.send_pfps.cancel()

    @tasks.loop(minutes=5)
    async def send_pfps(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        image_urls = []
        retries = 0
        while not image_urls and retries < 5:
            query = random.choice(self.search_queries)
            image_urls = await self.fetch_images(query)
            retries += 1
            if not image_urls:
                await asyncio.sleep(2)

        if image_urls:
            selected = random.sample(image_urls, min(5, len(image_urls)))
            embed = discord.Embed(color=discord.Color.dark_purple())
            for idx, url in enumerate(selected, start=1):
                embed.add_field(name=f"PFP {idx}", value=url, inline=False)
            await channel.send(embed=embed)

    @send_pfps.before_loop
    async def before_pfps(self):
        await self.bot.wait_until_ready()

    async def fetch_images(self, query):
        headers = {"User-Agent": "Mozilla/5.0"}
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
