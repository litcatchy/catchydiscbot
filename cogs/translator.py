import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled_guilds = {}  # Dictionary to store enabled guilds

    async def send_embed(self, ctx, description, color):
        embed = discord.Embed(description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="translator")
    async def translator(self, ctx, mode: str):
        """Turn on or off the auto-translation feature. Only the server owner can use this."""
        if not ctx.author == ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn it on or off.", discord.Color.red())

        if mode.lower() == "on":
            self.enabled_guilds[ctx.guild.id] = True
            return await self.send_embed(ctx, "<:success:1346853488738566175> Auto-translation enabled.", discord.Color.green())

        elif mode.lower() == "off":
            self.enabled_guilds[ctx.guild.id] = False
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Auto-translation disabled.", discord.Color.red())

        else:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Invalid option! Use `,translator on` or `,translator off`.", discord.Color.red())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        guild_id = message.guild.id
        if guild_id not in self.enabled_guilds or not self.enabled_guilds[guild_id]:
            return  # If translation is off, do nothing

        try:
            detected_lang = detect(message.content)  # Detect language

            # Ignore messages already in English unless they look like English but are not
            if detected_lang == "en":
                return

            translated_text = GoogleTranslator(source="auto", target="en").translate(message.content)

            if translated_text and translated_text.lower() != message.content.lower():
                embed = discord.Embed(
                    description=f"**Original:** {message.content}\n➡ **Translated:** {translated_text}",
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)

        except Exception as e:
            print(f"Translation Error: {e}")

async def setup(bot):
    await bot.add_cog(Translator(bot))
