import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Confession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="confession", description="Make an anonymous confession")
    @app_commands.describe(title="Your confession title", message="Type your confession here (1000 characters max)")
    async def confession(self, interaction: discord.Interaction, title: str, message: str):
        await interaction.response.defer(thinking=False, ephemeral=True)

        # Channels
        confession_channel = interaction.guild.get_channel(1349126675555815555)
        log_channel = interaction.guild.get_channel(1358510593950224495)

        if not confession_channel or not log_channel:
            await interaction.followup.send("Confession channels are not set correctly. Please contact the admin.", ephemeral=True)
            return

        # Prepare confession embed
        confession_embed = discord.Embed(
            title="New confession:",
            description=f"**{title}**\n{message}",
            color=discord.Color.from_str("#FFB6C1"),
            timestamp=datetime.datetime.utcnow()
        )
        confession_embed.set_footer(text="Use /confession to make anonymous confessions.")

        # Prepare log embed
        log_embed = discord.Embed(
            title="Confession Log",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        log_embed.add_field(name="User", value=f"{interaction.user} (ID: {interaction.user.id})", inline=False)
        log_embed.add_field(name="Guild", value=f"{interaction.guild.name} (ID: {interaction.guild.id})", inline=False)
        log_embed.add_field(name="Confession Title", value=title, inline=False)
        log_embed.add_field(name="Confession Message", value=message, inline=False)

        # Send confession to confession channel
        await confession_channel.send(embed=confession_embed)

        # Send log to log channel
        await log_channel.send(embed=log_embed)

        # Send confirmation to the user
        await interaction.followup.send("Your confession has been sent anonymously.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Confession(bot))
