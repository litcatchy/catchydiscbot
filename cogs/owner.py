import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, title, description, color):
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        """Reloads a specific cog. Only the bot owner can use this."""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await self.bot.load_extension(f"cogs.{extension}")
            await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                  f"Reloaded `{extension}` cog.", discord.Color.green())
        except Exception as e:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  f"Failed to reload `{extension}` cog.\n```{e}```", discord.Color.red())

async def setup(bot):
    await bot.add_cog(Owner(bot))
