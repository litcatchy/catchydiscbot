import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        """Reloads a specific cog. Only the bot owner can use this."""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await self.bot.load_extension(f"cogs.{extension}")
            await ctx.send(f"✅ Successfully reloaded `{extension}` cog.")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{extension}` cog.\n```{e}```")

async def setup(bot):
    await bot.add_cog(Owner(bot))
