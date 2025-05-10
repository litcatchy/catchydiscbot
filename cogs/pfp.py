import discord
from discord.ext import commands, tasks
import random
import aiohttp
import io
from bs4 import BeautifulSoup

class PFPSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1362801674560737462
        self.query_list = [
            "femboy anime aesthetic pfp site:pinterest.com",
            "goth girl aesthetic pfp site:pinterest.com",
            "dark romance aesthetic pfp site:pinterest.com",
            "aesthetic girl tied up pfp site:pinterest.com",
            "yandere anime girl pfp site:pinterest.com",
            "emo aesthetic anime pfp site:pinterest.com",
            "alt aesthetic anime pfp site:pinterest.com",
            "money aesthetic anime pfp site:pinterest.com",
            "crazy anime girl aesthetic pfp site:pinterest.com",
            "soft bloody cute anime pfp site:pinterest.com",
            "normal egirl aesthetic pfp discord site:pinterest.com",
            "normal eboy aesthetic pfp discord site:pinterest.com",
            "cat girl aesthetic pfp site:pinterest.com"
        ]
        self.send_pfps.start()

    def cog_unload(self):
        self.send_pfps.cancel()

    async def fetch_images(self, query, count=5):
        url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        images = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    pins = soup.find_all('img', {'srcset': True})
                    for pin in pins:
                        img_url = pin['srcset'].split(',')[0].split(' ')[0]  # Get the largest image
                        images.append(img_url)
                        if len(images) == count:
                            break
            except Exception as e:
                print(f"Error fetching images: {e}")
        return images

    @tasks.loop(minutes=5)
    async def send_pfps(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        query = random.choice(self.query_list)
        image_urls = []

        while len(image_urls) < 5:
            results = await self.fetch_images(query)
            for img in results:
                if img not in image_urls:
                    image_urls.append(img)
                if len(image_urls) == 5:
                    break
            if len(image_urls) < 5:
                query = random.choice(self.query_list)

        files = []
        async with aiohttp.ClientSession() as session:
            for url in image_urls:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            img_bytes = await resp.read()
                            filename = url.split("/")[-1].split("?")[0]
                            files.append(discord.File(io.BytesIO(img_bytes), filename=filename))
                except:
                    continue

        if files:
            await channel.send(files=files)

async def setup(bot):
    await bot.add_cog(PFPSpam(bot))
