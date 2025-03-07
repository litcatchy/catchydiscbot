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

            embed = discord.Embed(
                title="Cog Reloaded",
                description=f"{self.bot.success_emoji} Successfully reloaded `{extension}` cog.",
                color=discord.Color.green()
            )
        except Exception as e:
            embed = discord.Embed(
                title="Reload Failed",
                description=f"{self.bot.cancel_emoji} Failed to reload `{extension}` cog.\n```{e}```",
                color=discord.Color.red()
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Owner(bot))
