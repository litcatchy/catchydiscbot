import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translation_enabled = {}  # Dictionary to track per-guild settings

    async def send_embed(self, ctx, description, color):
        embed = discord.Embed(description=description, color=color)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        guild_id = message.guild.id
        if not self.translation_enabled.get(guild_id, False):
            return  # Ignore if translation is disabled

        try:
            detected_lang = detect(message.content)

            if detected_lang != "en":  # Only translate non-English messages
                translated_text = GoogleTranslator(source="auto", target="en").translate(message.content)
                embed = discord.Embed(
                    description=f"**Original:** {message.content}\n➡ **Translated:** {translated_text}",
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
        except Exception as e:
            print(f"Translation error: {e}")

    @commands.command(name="on")
    async def enable_translation(self, ctx):
        """Enable automatic translation (Server Owner Only)"""
        if ctx.author != ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn this on or off.", discord.Color.red())

        self.translation_enabled[ctx.guild.id] = True
        await self.send_embed(ctx, "<:success:1346853488738566175> Automatic translation enabled.", discord.Color.green())

    @commands.command(name="off")
    async def disable_translation(self, ctx):
        """Disable automatic translation (Server Owner Only)"""
        if ctx.author != ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn this on or off.", discord.Color.red())

        self.translation_enabled[ctx.guild.id] = False
        await self.send_embed(ctx, "<:success:1346853488738566175> Automatic translation disabled.", discord.Color.green())

async def setup(bot):
    await bot.add_cog(Translator(bot))
