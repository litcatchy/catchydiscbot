import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
import langdetect

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translation_enabled = {}

    async def send_embed(self, ctx, description, color):
        embed = discord.Embed(description=description, color=color)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        if not self.translation_enabled.get(guild_id, False):
            return

        try:
            detected_lang = langdetect.detect(message.content)
            if detected_lang != "en":
                translated_text = GoogleTranslator(source="auto", target="en").translate(message.content)
                embed = discord.Embed(description=f"**{message.content}** → **{translated_text}**", color=discord.Color.blue())
                await message.channel.send(embed=embed)
        except Exception:
            pass  # Ignore errors if detection or translation fails

    @commands.command(name="on")
    async def enable_translation(self, ctx):
        """Enables automatic translation. Only the server owner can use this."""
        if ctx.guild.owner_id != ctx.author.id:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn this on or off.", discord.Color.red())

        self.translation_enabled[ctx.guild.id] = True
        await self.send_embed(ctx, "<:success:1346853488738566175> Translation has been enabled.", discord.Color.green())

    @commands.command(name="off")
    async def disable_translation(self, ctx):
        """Disables automatic translation. Only the server owner can use this."""
        if ctx.guild.owner_id != ctx.author.id:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn this on or off.", discord.Color.red())

        self.translation_enabled[ctx.guild.id] = False
        await self.send_embed(ctx, "<:success:1346853488738566175> Translation has been disabled.", discord.Color.green())

async def setup(bot):
    await bot.add_cog(Translator(bot))
