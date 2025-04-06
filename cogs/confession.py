import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class ConfessionModal(discord.ui.Modal, title="Make a Confession"):
    confession_title = discord.ui.TextInput(
        label="Your confession title",
        placeholder="Enter the title of your confession",
        max_length=100
    )
    confession_message = discord.ui.TextInput(
        label="Type your confession here",
        style=discord.TextStyle.paragraph,
        placeholder="Write your confession (max 1000 characters)",
        max_length=1000
    )

    def __init__(self, bot: commands.Bot, interaction: discord.Interaction):
        super().__init__()
        self.bot = bot
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        confession_channel_id = 1349126675555815555
        log_channel_id = 1358510593950224495

        confession_channel = self.bot.get_channel(confession_channel_id)
        log_channel = self.bot.get_channel(log_channel_id)

        confession_embed = discord.Embed(
            title="New confession",
            description=f"**Confession:**\n{self.confession_message.value}",
            color=discord.Color.from_str("#FFC0CB")  # Light pink
        )
        confession_embed.set_footer(text="Use /confession to make anonymous confessions.")

        log_embed = discord.Embed(
            title="Confession Log",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        log_embed.add_field(name="User", value=f"{self.interaction.user} ({self.interaction.user.id})", inline=False)
        log_embed.add_field(name="Confession Title", value=self.confession_title.value, inline=False)
        log_embed.add_field(name="Confession", value=self.confession_message.value, inline=False)

        try:
            await confession_channel.send(embed=confession_embed)
            await log_channel.send(embed=log_embed)
            await interaction.response.send_message("Your confession has been sent!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while sending your confession.", ephemeral=True)

class Confession(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.confession_cooldown = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.user)  # 5 mins cooldown

    @app_commands.command(name="confession", description="Send an anonymous confession")
    async def confession(self, interaction: discord.Interaction):
        bucket = self.confession_cooldown.get_bucket(interaction)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            await interaction.response.send_message(
                f"You are on cooldown. Please try again in {int(retry_after)} seconds.",
                ephemeral=True
            )
            return

        modal = ConfessionModal(self.bot, interaction)
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Confession(bot))
