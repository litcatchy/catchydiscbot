import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_translate = {}  # Dictionary to store per-server translation status

    async def send_embed(self, ctx, description, color):
        """Sends an embed message."""
        embed = discord.Embed(description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="translator")
    async def translator_command(self, ctx, action: str):
        """Enables or disables automatic translation (Server owner only)."""
        if ctx.author != ctx.guild.owner:
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Only the server owner can turn it on or off.", discord.Color.red())

        if action.lower() == "on":
            self.auto_translate[ctx.guild.id] = True
            await self.send_embed(ctx, "<:success:1346853488738566175> Automatic translation has been enabled.", discord.Color.green())

        elif action.lower() == "off":
            self.auto_translate[ctx.guild.id] = False
            await self.send_embed(ctx, "<:success:1346853488738566175> Automatic translation has been disabled.", discord.Color.green())

        else:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Invalid command! Use `,translator on` or `,translator off`.", discord.Color.red())

    @commands.Cog.listener()
    async def on_message(self, message):
        """Detects and translates non-English messages."""
        if message.author.bot or message.guild is None:
            return  # Ignore bot messages and DMs

        if self.auto_translate.get(message.guild.id, False):  # Check if translation is enabled
            try:
                detected_lang = detect(message.content)

                if detected_lang != "en":
                    translated_text = GoogleTranslator(source="auto", target="en").translate(message.content)

                    if translated_text.lower() != message.content.lower():  # Avoid unnecessary messages
                        embed = discord.Embed(
                            description=f"**Original:** {message.content}\n**➜ Translated:** {translated_text}",
                            color=discord.Color.blue()
                        )
                        await message.channel.send(embed=embed)
            except Exception as e:
                print(f"Translation Error: {e}")

async def setup(bot):
    await bot.add_cog(Translator(bot))
