import discord from discord.ext import commands, tasks from discord import app_commands import asyncio

class VCControlView(discord.ui.View): def init(self, bot): super().init(timeout=None) self.bot = bot

async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message(
            embed=discord.Embed(
                description="<:cancel:1346853536738316339> You must be connected to a voice channel to use this.",
                color=discord.Color.red()
            ), ephemeral=True
        )
        return False
    return True

@discord.ui.button(label="Lock", style=discord.ButtonStyle.red, custom_id="vc_lock")
async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.connect = False
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel locked.", ephemeral=True)

@discord.ui.button(label="Unlock", style=discord.ButtonStyle.green, custom_id="vc_unlock")
async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.connect = True
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel unlocked.", ephemeral=True)

@discord.ui.button(label="Hide", style=discord.ButtonStyle.red, custom_id="vc_hide")
async def hide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.view_channel = False
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel hidden.", ephemeral=True)

@discord.ui.button(label="Reveal", style=discord.ButtonStyle.green, custom_id="vc_reveal")
async def reveal_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.view_channel = True
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel revealed.", ephemeral=True)

@discord.ui.button(label="Rename", style=discord.ButtonStyle.blurple, custom_id="vc_rename")
async def rename_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message("Send the new name in chat.", ephemeral=True)

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        await interaction.user.voice.channel.edit(name=msg.content)
        await msg.reply("Voice channel renamed.", delete_after=5)
    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to respond.", ephemeral=True)

@discord.ui.button(label="Increase", style=discord.ButtonStyle.gray, custom_id="vc_increase")
async def increase_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    limit = vc.user_limit + 1 if vc.user_limit else 2
    await vc.edit(user_limit=limit)
    await interaction.response.send_message(f"User limit increased to {limit}.", ephemeral=True)

@discord.ui.button(label="Decrease", style=discord.ButtonStyle.gray, custom_id="vc_decrease")
async def decrease_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if vc.user_limit and vc.user_limit > 0:
        new_limit = vc.user_limit - 1
        await vc.edit(user_limit=new_limit)
        await interaction.response.send_message(f"User limit decreased to {new_limit}.", ephemeral=True)
    else:
        await interaction.response.send_message("User limit is already at minimum.", ephemeral=True)

@discord.ui.button(label="Claim", style=discord.ButtonStyle.blurple, custom_id="vc_claim")
async def claim_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if vc.members and vc.members[0] != interaction.user:
        await vc.edit(name=f"{interaction.user.name}'s VC")
        await interaction.response.send_message("You claimed the voice channel.", ephemeral=True)
    else:
        await interaction.response.send_message("You're already the first member in this VC.", ephemeral=True)

@discord.ui.button(label="Transfer", style=discord.ButtonStyle.gray, custom_id="vc_transfer")
async def transfer_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message("Mention the user to transfer ownership to.", ephemeral=True)

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        if msg.mentions:
            target = msg.mentions[0]
            await interaction.user.voice.channel.edit(name=f"{target.name}'s VC")
            await msg.reply("Ownership transferred.", delete_after=5)
        else:
            await msg.reply("No user mentioned.", delete_after=5)
    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to respond.", ephemeral=True)

@discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id="vc_delete")
async def delete_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    await vc.delete(reason=f"Deleted by {interaction.user}")
    await interaction.response.send_message("Voice channel deleted.", ephemeral=True)

class VCControl(commands.Cog): def init(self, bot): self.bot = bot self.panel_message = None self.send_panel.start()

def cog_unload(self):
    self.send_panel.cancel()

@tasks.loop(hours=4)
async def send_panel(self):
    await self.bot.wait_until_ready()
    channel = self.bot.get_channel(1362754109454680225)
    if channel is None:
        return

    async for msg in channel.history(limit=10):
        if msg.author == self.bot.user and msg.components:
            try:
                await msg.delete()
            except:
                pass

    embed = discord.Embed(
        title="Voice Channel Controls",
        description="Use the buttons below to manage your voice channel.",
        color=discord.Color.blurple()
    )
    view = VCControlView(self.bot)
    self.panel_message = await channel.send(embed=embed, view=view)

@send_panel.before_loop
async def before_panel(self):
    await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(VCControl(bot))

