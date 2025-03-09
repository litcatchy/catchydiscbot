import discord
from discord.ext import commands
from deep_translator import GoogleTranslator

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator_enabled = {}  # Dictionary to store per-server setting

    def detect_language(self, text):
        """Detects the language of a given text."""
        return GoogleTranslator(source="auto", target="en").detect(text)

    def translate_to_english(self, text):
        """Translates text to English."""
        return GoogleTranslator(source="auto", target="en").translate(text)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks messages and translates non-English ones."""
        if message.author.bot or not message.guild:
            return  # Ignore bot messages and DMs

        guild_id = message.guild.id
        if not self.translator_enabled.get(guild_id, False):
            return  # Skip if translation is disabled

        lang = self.detect_language(message.content)
        if lang != "en":
            translated_text = self.translate_to_english(message.content)
            embed = discord.Embed(description=f"**{message.content} → {translated_text}**", color=discord.Color.blue())
            await message.channel.send(embed=embed)

    @commands.command(name="on")
    async def enable_translator(self, ctx, setting: str):
        """Enables the translation feature. Only for server owners."""
        if ctx.author != ctx.guild.owner:
            return await ctx.send("<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")

        if setting.lower() == "translator":
            self.translator_enabled[ctx.guild.id] = True
            await ctx.send("<:success:1346853488738566175> Translator has been enabled.")

    @commands.command(name="off")
    async def disable_translator(self, ctx, setting: str):
        """Disables the translation feature. Only for server owners."""
        if ctx.author != ctx.guild.owner:
            return await ctx.send("<:cancel:1346853536738316339> Skill issue, slaves cannot use the command on the server owner")

        if setting.lower() == "translator":
            self.translator_enabled[ctx.guild.id] = False
            await ctx.send("<:success:1346853488738566175> Translator has been disabled.")

async def setup(bot):
    await bot.add_cog(Translator(bot))
