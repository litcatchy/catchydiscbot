import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translation_enabled = {}

    async def send_embed(self, ctx, description, color=discord.Color.green()):
        embed = discord.Embed(description=description, color=color)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Detects and translates non-English messages."""
        if message.author.bot or not message.guild:
            return  # Ignore bot messages and DMs
        
        guild_id = message.guild.id
        if not self.translation_enabled.get(guild_id, False):
            return  # Ignore if translation is disabled for this server

        try:
            detected_lang = detect(message.content)  # Detect the language
            if detected_lang == "en":
                return  # Ignore English messages

            # Translate the message
            translated_text = GoogleTranslator(source="auto", target="en").translate(message.content)

            # Send translation in an embed
            embed = discord.Embed(
                description=f"**Original:** {message.content}\n**→ Translated:** {translated_text}",
                color=discord.Color.blue()
            )
            await message.channel.send(embed=embed)

        except Exception as e:
            print(f"Translation error: {e}")

    @commands.command(name="on_translator")
    async def enable_translation(self, ctx):
        """Enable automatic translation (Server Owner Only)."""
        if ctx.guild.owner_id != ctx.author.id:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn it on.", discord.Color.red())

        self.translation_enabled[ctx.guild.id] = True
        await self.send_embed(ctx, "<:success:1346853488738566175> Translator has been enabled!")

    @commands.command(name="off_translator")
    async def disable_translation(self, ctx):
        """Disable automatic translation (Server Owner Only)."""
        if ctx.guild.owner_id != ctx.author.id:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn it off.", discord.Color.red())

        self.translation_enabled[ctx.guild.id] = False
        await self.send_embed(ctx, "<:success:1346853488738566175> Translator has been disabled!")

async def setup(bot):
    await bot.add_cog(Translator(bot))
