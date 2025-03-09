import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect
import re

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator_enabled = True  # Default state is ON

    def is_english(self, text):
        """Detect if the message is in English or another language."""
        try:
            lang = detect(text)

            # If the detected language is English, check if it contains non-Latin characters
            if lang == 'en':
                if re.search(r'[^\x00-\x7F]+', text):  # Detects non-ASCII characters (non-Latin scripts)
                    return False  # Treats English words in non-Latin script as a different language
                return True  # If it’s pure English, return True

            return False  # If the language is not English, return False
        except Exception as e:
            print(f"Language detection error: {e}")
            return False  # If detection fails, assume it's non-English

    async def translate_message(self, message):
        """Translate non-English messages into English."""
        if not self.is_english(message.content):  # If message is NOT in English, translate it
            translated = GoogleTranslator(source='auto', target='en').translate(message.content)

            embed = discord.Embed(
                description=f"**Original:** {message.content}\n**Translated:** {translated}",
                color=discord.Color.blue()
            )
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Detects messages and translates if necessary."""
        if message.author.bot or not self.translator_enabled:
            return  # Ignore bot messages and if translator is off

        await self.translate_message(message)  # Translate message if needed

    @commands.command(name="on translator")
    async def enable_translator(self, ctx):
        """Enable the translator. Only the server owner can use this."""
        if ctx.guild.owner_id != ctx.author.id:
            return await ctx.send("<:cancel:1346853536738316339> Only the server owner can turn it on or off.")
        
        self.translator_enabled = True
        await ctx.send("<:success:1346853488738566175> Translator feature enabled.")

    @commands.command(name="off translator")
    async def disable_translator(self, ctx):
        """Disable the translator. Only the server owner can use this."""
        if ctx.guild.owner_id != ctx.author.id:
            return await ctx.send("<:cancel:1346853536738316339> Only the server owner can turn it on or off.")

        self.translator_enabled = False
        await ctx.send("<:success:1346853488738566175> Translator feature disabled.")

async def setup(bot):
    await bot.add_cog(Translator(bot))
