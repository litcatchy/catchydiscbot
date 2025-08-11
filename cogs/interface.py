import discord
from discord.ext import commands, tasks
import asyncio

class VCControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.owners = {}  # Track VC owners manually
        self.protected_vcs = set()  # Track protected VCs

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
        await vc.edit(name=f"{interaction.user.name}'s VC")
        self.owners[vc.id] = interaction.user.id
        await interaction.response.send_message("You claimed the voice channel.", ephemeral=True)

    @discord.ui.button(label="Transfer", style=discord.ButtonStyle.secondary, custom_id="vc_transfer")
    async def transfer_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice.channel
        if self.owners.get(vc.id) != interaction.user.id:
            await interaction.response.send_message("You must be the owner of the voice channel to transfer ownership.", ephemeral=True)
            return

        members = [member for member in vc.members if member != interaction.user]
        if not members:
            await interaction.response.send_message("No one else is in the VC to transfer ownership to.", ephemeral=True)
            return

        options = [discord.SelectOption(label=member.name, value=str(member.id)) for member in members]

        select = discord.ui.Select(
            placeholder="Choose a person to transfer ownership",
            options=options
        )

        async def transfer_callback(i: discord.Interaction):
            new_owner_id = int(i.data['values'][0])
            self.owners[vc.id] = new_owner_id
            await i.response.send_message("Ownership transferred successfully.", ephemeral=True)

        select.callback = transfer_callback
        await interaction.response.send_message("Please select who to transfer ownership to.", ephemeral=True, view=discord.ui.View(select))

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, custom_id="vc_disconnect")
    async def disconnect_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice.channel
        if self.owners.get(vc.id) != interaction.user.id:
            await interaction.response.send_message("You must be the owner of the voice channel to disconnect a member.", ephemeral=True)
            return

        members = [member for member in vc.members if member != interaction.user]
        if not members:
            await interaction.response.send_message("No one to disconnect.", ephemeral=True)
            return

        options = [discord.SelectOption(label=member.name, value=str(member.id)) for member in members]

        select = discord.ui.Select(
            placeholder="Choose a person to disconnect",
            options=options
        )

        async def disconnect_callback(i: discord.Interaction):
            member_id = int(i.data['values'][0])
            member = i.guild.get_member(member_id)
            if member:
                await member.move_to(None)
                await i.response.send_message(f"{member.name} has been disconnected.", ephemeral=True)

        select.callback = disconnect_callback
        await interaction.response.send_message("Please select who to disconnect.", ephemeral=True, view=discord.ui.View(select))

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.secondary, custom_id="vc_delete")
    async def delete_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice.channel
        if vc.id != 1401547369773793304 and vc.id not in self.protected_vcs:
            await vc.delete(reason=f"Deleted by {interaction.user}")
            await interaction.response.send_message("Voice channel deleted.", ephemeral=True)
        elif vc.id in self.protected_vcs:
            await interaction.response.send_message("This voice channel is protected and cannot be deleted.", ephemeral=True)
        else:
            await interaction.response.send_message("This voice channel cannot be deleted.", ephemeral=True)

    @discord.ui.button(label="Protect", style=discord.ButtonStyle.secondary, custom_id="vc_protect")
    async def protect_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice.channel
        if self.owners.get(vc.id) != interaction.user.id:
            await interaction.response.send_message("Only the VC owner can toggle protection.", ephemeral=True)
            return

        if vc.id in self.protected_vcs:
            self.protected_vcs.remove(vc.id)
            await interaction.response.send_message("Voice channel is no longer protected.", ephemeral=True)
        else:
            self.protected_vcs.add(vc.id)
            await interaction.response.send_message("Voice channel is now protected from deletion.", ephemeral=True)

class VCControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.panel_message = None
        self.send_panel.start()

    def cog_unload(self):
        self.send_panel.cancel()

    @tasks.loop(hours=4)
    async def send_panel(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(1401547369773793304)
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

Buttons:
Lock - Lock your voice channel
Unlock - Unlock your voice channel
Hide - Hide your voice channel
Reveal - Reveal your voice channel
Increase - Increase your voice channel's user limit
Decrease - Decrease your voice channel's user limit
Claim - Claim your voice channel
Transfer - Transfer ownership of your voice channel
Disconnect - Disconnect a member from the voice channel
Delete - Delete your voice channel
Protect - Toggle VC deletion protection""",
            color=discord.Color.blurple()
        )
        view = VCControlView(self.bot)
        self.panel_message = await channel.send(embed=embed, view=view)

    @send_panel.before_loop
    async def before_panel(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == 1401547369773793304:
            category = self.bot.get_channel(1401547369773793302)
            if category:
                new_vc = await member.guild.create_voice_channel(
                    f"{member.name}'s VC", category=category)
                await new_vc.set_permissions(member, connect=True)
                await member.move_to(new_vc)

        # Deletion of empty VCs created from the make-a-vc channel
        if before.channel and before.channel.id != 1401547369773793304:
            if before.channel.category and before.channel.category.id == 1401547369773793302:
                if len(before.channel.members) == 0 and before.channel.id != 1401547369773793304:
                    try:
                        await before.channel.delete(reason="Auto-deleted empty VC")
                    except:
                        pass

# Add the setup function
async def setup(bot):
    await bot.add_cog(VCControl(bot))
