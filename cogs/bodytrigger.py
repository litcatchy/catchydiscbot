import discord
from discord.ext import commands
import re
import random

class PFPTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.triggers = {
            r"\blips?\b": [
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371141905005674617/94d586bb5680e5be1fcc7fbc2e4ac71b.jpg?ex=68220ee8&is=6820bd68&hm=95b70ca1fcd46d5989744bae5fcc0a9ae3227ff229e4145b556ae97e313ca200&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371141094531661894/7de72e735d5247283916d54aa34f2765.jpg?ex=68220e27&is=6820bca7&hm=7ae128477b30e842346b7b2cb046bc489b3196654f3e797645baa401918efdcb&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371142194014060776/919c21c33540b0ec73678740512ba850.jpg?ex=68220f2d&is=6820bdad&hm=3934d3f6dc7bb066989357fe691c40a9fd57ca9e976939b194aa6fe04c9076d3&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371142639306543295/a06bb3bc971964144554967a5ba36dfc.jpg?ex=68220f97&is=6820be17&hm=1fe83bd948f6fe62c7353d54018eb7ffa378e7096bfdc5f20b6005e7e61aae0e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371142900758478938/a4ab707b3f5e7d7e1e9f6f5ac1a3b96a.jpg?ex=68220fd6&is=6820be56&hm=6126aab43185429e7a79bd78bdd9c8cebff60e056772cbb72c439b315079c058&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371143315344330772/078143f7d50e0b227bfa6897aca137b8.jpg?ex=68221038&is=6820beb8&hm=1ab1b53e31cbe14319a5340ecf5c9ded943a054e563afc63140cb8aa7fac22fa&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371143505585504276/IMG_20250511_204438.jpg?ex=68221066&is=6820bee6&hm=60daf14ac82c03a772ed30a5df170872675abd103d210976a132e2578f20676c&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144002044166296/1dacb85561f831418b4cdf7ecfda1e1e.jpg?ex=682210dc&is=6820bf5c&hm=fa96ddb00430e764d5a813d425cc68e57ba39c93b050f09b2d144f973855ae0e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144002044166296/1dacb85561f831418b4cdf7ecfda1e1e.jpg?ex=682210dc&is=6820bf5c&hm=fa96ddb00430e764d5a813d425cc68e57ba39c93b050f09b2d144f973855ae0e&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144238745780267/6b15673c6fb03f5aed0c8ce88feaea05.jpg?ex=68221115&is=6820bf95&hm=919f4258a09606888de912d63d6d4f3cda1a054eecb71d73bd7b27fdd8fe3728&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144253366861874/03c8ae2982747a0a755d549090f37530.jpg?ex=68221118&is=6820bf98&hm=61eb726a496ec8c131a3cb021e9f22c599038404ae3752eaaab1570eef2e7de9&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371144264465256558/6a6ba9e582ec4e07e9904da3899fe061.jpg?ex=6822111b&is=6820bf9b&hm=6f79a4d4306d0caabe06b6be67dc99753d0e759eb40c67d3204b99023ea922bd&",         
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
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371141094531661894/7de72e735d5247283916d54aa34f2765.jpg?ex=68220e27&is=6820bca7&hm=7ae128477b30e842346b7b2cb046bc489b3196654f3e797645baa401918efdcb&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146362149802054/IMG_20250511_205454.jpg?ex=6822130f&is=6820c18f&hm=f4a6a96f9cb39879af7b194dd7dbb8338f0510d3a7baaaf83bb007020c187402&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146351588675654/b58c96ec0785ef7a3c511dfa9d51864a.jpg?ex=6822130c&is=6820c18c&hm=73519d91fdff71bf200973edb7e7be0ad0b7b27573ee0651de541c5541a409e9&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146374896422982/c2789544d03bb27dbb232c03b943fb66.jpg?ex=68221312&is=6820c192&hm=112d68bd9c177ff45e0e3094510a8597831f688d7b8b9073c65f419618cff98d&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146387470811326/633cc3a55c343fa83840fe79c48845cf.jpg?ex=68221315&is=6820c195&hm=d591c5fefa9565a9723e4c69577b10a876545cc75520d6f7f40d83bc4cf113c0&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146422891843715/589eddc62b728289eaf4dead084276bb.jpg?ex=6822131d&is=6820c19d&hm=e85f81fc60c8c1a264d77cffbd2e4647c3666103006bac8a91f996d5c309ed20&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146400947114094/26c0ddd3ad777b805dc7cd1037da8944.jpg?ex=68221318&is=6820c198&hm=0c1a0520dc8ead1dcdd31dffa8bafa713169f87610e730215dd1a075f803346b&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146533042389123/7040ef8647c1909161989ed91aadfc75.jpg?ex=68221338&is=6820c1b8&hm=ce5dacbc9cf1da7cfb9716fc3611a6f4b834eff194166c8e4fad88d3141cfcf6&",
                "https://cdn.discordapp.com/attachments/1371136109479858296/1371146544153235567/c07d1030aa0c62cd5df2219b32b2fe7f.jpg?ex=6822133a&is=6820c1ba&hm=661bed317a664598b6c957739254ae0d00600dac818f4209dbe12b8ce47c66df&",
                "https://cdn.discordapp.com/attachments/123456/eyes1.png",
                "https://cdn.discordapp.com/attachments/123456/eyes2.png",
                "https://cdn.discordapp.com/attachments/123456/eyes3.png",
                "https://cdn.discordapp.com/attachments/123456/eyes1.png",
                "https://cdn.discordapp.com/attachments/123456/eyes2.png",
                "https://cdn.discordapp.com/attachments/123456/eyes3.png",
                "https://cdn.discordapp.com/attachments/123456/eyes1.png",
                "https://cdn.discordapp.com/attachments/123456/eyes2.png",
                "https://cdn.discordapp.com/attachments/123456/eyes3.png",
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
