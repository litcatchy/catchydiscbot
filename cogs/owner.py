import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, title, description, color):
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="reload")
    async def reload(self, ctx, extension: str):
        """Reloads a specific cog. Only the bot owner can use this."""
        if not await self.bot.is_owner(ctx.author):
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                         "Only the bot owner can reload cogs.", discord.Color.red())

        cog_name = f"cogs.{extension}"

        if cog_name not in self.bot.extensions:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                         f"Extension `{extension}` has not been loaded.", discord.Color.red())

        try:
            # Unload & reload the cog
            await self.bot.unload_extension(cog_name)
            await self.bot.load_extension(cog_name)
            await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                  f"Reloaded `{extension}` cog.", discord.Color.green())
        except Exception as e:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  f"Failed to reload `{extension}` cog.\n```{e}```", discord.Color.red())

async def setup(bot):
    await bot.add_cog(Owner(bot))
