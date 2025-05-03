import discord
from discord.ext import commands

class ServerList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="myservers")
    @commands.is_owner()
    async def myservers(self, ctx):
        servers = [f"{guild.name} (ID: {guild.id})" for guild in self.bot.guilds]
        await ctx.author.send("I’m in these servers:\n" + "\n".join(servers))

async def setup(bot):
    await bot.add_cog(ServerList(bot))
