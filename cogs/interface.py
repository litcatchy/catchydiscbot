import discord from discord.ext import commands, tasks import asyncio

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

def is_vc_owner(self, user: discord.Member, vc: discord.VoiceChannel):
    return vc.topic == str(user.id)

@discord.ui.button(label="Lock", style=discord.ButtonStyle.secondary, custom_id="vc_lock")
async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the voice channel owner can lock it.", ephemeral=True)
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.connect = False
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel locked.", ephemeral=True)

@discord.ui.button(label="Unlock", style=discord.ButtonStyle.secondary, custom_id="vc_unlock")
async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the voice channel owner can unlock it.", ephemeral=True)
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.connect = True
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel unlocked.", ephemeral=True)

@discord.ui.button(label="Hide", style=discord.ButtonStyle.secondary, custom_id="vc_hide")
async def hide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the voice channel owner can hide it.", ephemeral=True)
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.view_channel = False
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel hidden.", ephemeral=True)

@discord.ui.button(label="Reveal", style=discord.ButtonStyle.secondary, custom_id="vc_reveal")
async def reveal_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the voice channel owner can reveal it.", ephemeral=True)
    overwrite = vc.overwrites_for(interaction.guild.default_role)
    overwrite.view_channel = True
    await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("Voice channel revealed.", ephemeral=True)

@discord.ui.button(label="Increase", style=discord.ButtonStyle.secondary, custom_id="vc_increase")
async def increase_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the voice channel owner can increase the limit.", ephemeral=True)
    limit = vc.user_limit + 1 if vc.user_limit else 2
    await vc.edit(user_limit=limit)
    await interaction.response.send_message(f"User limit increased to {limit}.", ephemeral=True)

@discord.ui.button(label="Decrease", style=discord.ButtonStyle.secondary, custom_id="vc_decrease")
async def decrease_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the voice channel owner can decrease the limit.", ephemeral=True)
    if vc.user_limit and vc.user_limit > 0:
        new_limit = vc.user_limit - 1
        await vc.edit(user_limit=new_limit)
        await interaction.response.send_message(f"User limit decreased to {new_limit}.", ephemeral=True)
    else:
        await interaction.response.send_message("User limit is already at minimum.", ephemeral=True)

@discord.ui.button(label="Claim", style=discord.ButtonStyle.secondary, custom_id="vc_claim")
async def claim_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        await vc.edit(name=f"{interaction.user.name}'s VC", topic=str(interaction.user.id))
        await interaction.response.send_message("You claimed the voice channel.", ephemeral=True)
    else:
        await interaction.response.send_message("You're already the owner of this VC.", ephemeral=True)

@discord.ui.button(label="Transfer", style=discord.ButtonStyle.secondary, custom_id="vc_transfer")
async def transfer_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the VC owner can transfer ownership.", ephemeral=True)

    view = discord.ui.View()
    for member in vc.members:
        if member != interaction.user:
            view.add_item(discord.ui.Button(label=member.name, style=discord.ButtonStyle.primary, custom_id=f"transfer_{member.id}"))

    async def button_callback(interact: discord.Interaction):
        if not self.is_vc_owner(interact.user, vc):
            return await interact.response.send_message("You're not the owner anymore.", ephemeral=True)
        new_owner_id = int(interact.data['custom_id'].split('_')[1])
        await vc.edit(name=f"{vc.guild.get_member(new_owner_id).name}'s VC", topic=str(new_owner_id))
        await interact.response.send_message("Ownership transferred.", ephemeral=True)

    for child in view.children:
        if isinstance(child, discord.ui.Button):
            child.callback = button_callback

    await interaction.response.send_message("Choose a member to transfer ownership to:", view=view, ephemeral=True)

@discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, custom_id="vc_disconnect")
async def disconnect_member(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the VC owner can disconnect members.", ephemeral=True)

    view = discord.ui.View()
    for member in vc.members:
        if member != interaction.user:
            view.add_item(discord.ui.Button(label=member.name, style=discord.ButtonStyle.danger, custom_id=f"kick_{member.id}"))

    async def button_callback(interact: discord.Interaction):
        if not self.is_vc_owner(interact.user, vc):
            return await interact.response.send_message("You're not the owner anymore.", ephemeral=True)
        target_id = int(interact.data['custom_id'].split('_')[1])
        target = vc.guild.get_member(target_id)
        await target.move_to(None)
        await interact.response.send_message(f"{target.name} has been disconnected.", ephemeral=True)

    for child in view.children:
        if isinstance(child, discord.ui.Button):
            child.callback = button_callback

    await interaction.response.send_message("Select a member to disconnect:", view=view, ephemeral=True)

@discord.ui.button(label="Delete", style=discord.ButtonStyle.secondary, custom_id="vc_delete")
async def delete_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
    vc = interaction.user.voice.channel
    if not self.is_vc_owner(interaction.user, vc):
        return await interaction.response.send_message("Only the VC owner can delete this channel.", ephemeral=True)
    await vc.delete(reason=f"Deleted by {interaction.user}")
    await interaction.response.send_message("Voice channel deleted.", ephemeral=True)

class VCControl(commands.Cog): def init(self, bot): self.bot = bot self.panel_message = None self.send_panel.start()

def cog_unload(self):
    self.send_panel.cancel()

@tasks.loop(hours=5)
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
        description="""Use the buttons below to manage your voice channel.

Buttons: Lock - Lock your voice channel
Unlock - Unlock your voice channel Hide - Hide your voice channel Reveal - Reveal your voice channel Increase - Increase your voice channel's user limit Decrease - Decrease your voice channel's user limit Claim - Claim your voice channel Transfer - Transfer ownership of your voice channel Disconnect - Disconnect a user from your voice channel Delete - Delete your voice channel""", color=discord.Color.blurple() ) view = VCControlView(self.bot) self.panel_message = await channel.send(embed=embed, view=view)

@send_panel.before_loop
async def before_panel(self):
    await self.bot.wait_until_ready()

@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    if after.channel and after.channel.id == 1364639518279467079:
        category = self.bot.get_channel(1359208824497639424)
        if category:
            new_vc = await member.guild.create_voice_channel(
                f"{member.name}'s VC", category=category, topic=str(member.id))
            await new_vc.set_permissions(member, connect=True)
            await member.move_to(new_vc)
            await self.send_panel()
            await self.delete_inactive_vc(new_vc)

async def delete_inactive_vc(self, vc):
    await asyncio.sleep(600)
    if len(vc.members) == 0:
        await vc.delete()

async def setup(bot): await bot.add_cog(VCControl(bot))

