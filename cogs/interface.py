import discord from discord.ext import commands, tasks import asyncio

VC_CATEGORY_ID = 1359208824497639424 J2C_CHANNEL_ID = 1364639518279467079 PANEL_CHANNEL_ID = 1362754109454680225  # Replace with your text panel channel INACTIVITY_TIMEOUT = 600  # 10 minutes

class VCControlView(discord.ui.View): def init(self, bot): super().init(timeout=None) self.bot = bot

async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message(
            embed=discord.Embed(
                description="You must be connected to a voice channel to use this.",
                color=discord.Color.red()
            ), ephemeral=True
        )
        return False
    return True

@discord.ui.button(label="Lock", style=discord.ButtonStyle.secondary, custom_id="vc_lock")
async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.connect = False
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel locked.", ephemeral=True)

@discord.ui.button(label="Unlock", style=discord.ButtonStyle.secondary, custom_id="vc_unlock")
async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.connect = True
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel unlocked.", ephemeral=True)

@discord.ui.button(label="Hide", style=discord.ButtonStyle.secondary, custom_id="vc_hide")
async def hide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.view_channel = False
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel hidden.", ephemeral=True)

@discord.ui.button(label="Reveal", style=discord.ButtonStyle.secondary, custom_id="vc_reveal")
async def reveal_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.view_channel = True
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel revealed.", ephemeral=True)

@discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary, custom_id="vc_rename")
async def rename_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message(
        "Please rename your channel using the official Discord rename feature (forum modal).", ephemeral=True)

@discord.ui.button(label="Increase", style=discord.ButtonStyle.secondary, custom_id="vc_increase")
async def increase_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    limit = vc.user_limit + 1 if vc.user_limit else 2
    await vc.edit(user_limit=limit)
    await interaction.response.send_message(f"User limit increased to {limit}.", ephemeral=True)

@discord.ui.button(label="Decrease", style=discord.ButtonStyle.secondary, custom_id="vc_decrease")
async def decrease_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if vc.user_limit and vc.user_limit > 0:
        new_limit = vc.user_limit - 1
        await vc.edit(user_limit=new_limit)
        await interaction.response.send_message(f"User limit decreased to {new_limit}.", ephemeral=True)
    else:
        await interaction.response.send_message("User limit is already at minimum.", ephemeral=True)

@discord.ui.button(label="Claim", style=discord.ButtonStyle.secondary, custom_id="vc_claim")
async def claim_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if vc.members and vc.members[0] != interaction.user:
        await vc.edit(name=f"{interaction.user.name}'s VC")
        await interaction.response.send_message("You claimed the voice channel.", ephemeral=True)
    else:
        await interaction.response.send_message("You're already the first member in this VC.", ephemeral=True)

@discord.ui.button(label="Transfer", style=discord.ButtonStyle.secondary, custom_id="vc_transfer")
async def transfer_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_message(
        "Please use the official Discord forum to request ownership transfer.", ephemeral=True)

@discord.ui.button(label="Delete", style=discord.ButtonStyle.secondary, custom_id="vc_delete")
async def delete_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    await vc.delete(reason=f"Deleted by {interaction.user}")
    await interaction.response.send_message("Voice channel deleted.", ephemeral=True)

class VCControl(commands.Cog): def init(self, bot): self.bot = bot self.panel_message = None self.send_panel.start() self.inactivity_check.start()

def cog_unload(self):
    self.send_panel.cancel()
    self.inactivity_check.cancel()

@tasks.loop(hours=4)
async def send_panel(self):
    await self.bot.wait_until_ready()
    channel = self.bot.get_channel(PANEL_CHANNEL_ID)
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

@tasks.loop(seconds=60)
async def inactivity_check(self):
    await self.bot.wait_until_ready()
    guild = self.bot.guilds[0]  # Assumes the bot is only in one server
    for channel in guild.voice_channels:
        if channel.id == J2C_CHANNEL_ID:
            continue
        if channel.category_id != VC_CATEGORY_ID:
            continue
        if len(channel.members) == 0:
            last_active = channel.created_at.timestamp()
            now = discord.utils.utcnow().timestamp()
            if (now - last_active) > INACTIVITY_TIMEOUT:
                try:
                    await channel.delete(reason="Inactive temporary VC")
                except:
                    pass

@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    if after.channel and after.channel.id == J2C_CHANNEL_ID:
        guild = member.guild
        category = discord.utils.get(guild.categories, id=VC_CATEGORY_ID)
        vc = await guild.create_voice_channel(
            name=f"{member.name}'s VC",
            category=category,
            user_limit=5
        )
        await member.move_to(vc)

async def setup(bot): await bot.add_cog(VCControl(bot))

