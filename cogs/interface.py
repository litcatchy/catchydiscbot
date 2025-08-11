import discord
from discord.ext import commands

# --- CONFIG ---
MAKE_A_CALL_ID = 1401547369773793304       # VC where users join to make a new call
TEMP_CATEGORY_ID = 1401547369773793302     # Category where temp VCs will be made
CONTROL_PANEL_CHANNEL_ID = 1404367984168013854  # Text channel where buttons appear


class VCControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.owners = {}  # {vc_id: owner_id}

    def is_owner(self, interaction: discord.Interaction):
        owner_id = self.owners.get(interaction.channel.id)
        return owner_id == interaction.user.id

    @discord.ui.button(label="Lock VC", style=discord.ButtonStyle.danger)
    async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner(interaction):
            return await interaction.response.send_message("You’re not the VC owner.", ephemeral=True)

        await interaction.channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 VC locked.", ephemeral=True)

    @discord.ui.button(label="Unlock VC", style=discord.ButtonStyle.success)
    async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner(interaction):
            return await interaction.response.send_message("You’re not the VC owner.", ephemeral=True)

        await interaction.channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 VC unlocked.", ephemeral=True)

    @discord.ui.button(label="Rename VC", style=discord.ButtonStyle.primary)
    async def rename_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner(interaction):
            return await interaction.response.send_message("You’re not the VC owner.", ephemeral=True)

        modal = VCNameModal(interaction.channel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete VC", style=discord.ButtonStyle.danger)
    async def delete_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner(interaction):
            return await interaction.response.send_message("You’re not the VC owner.", ephemeral=True)

        await interaction.channel.delete(reason="Owner deleted VC")


class VCNameModal(discord.ui.Modal, title="Rename your VC"):
    def __init__(self, vc_channel):
        super().__init__()
        self.vc_channel = vc_channel

        self.new_name = discord.ui.TextInput(
            label="New VC Name",
            placeholder="Enter a new name...",
            max_length=30
        )
        self.add_item(self.new_name)

    async def on_submit(self, interaction: discord.Interaction):
        await self.vc_channel.edit(name=self.new_name.value)
        await interaction.response.send_message(f"✅ VC renamed to **{self.new_name.value}**", ephemeral=True)


class VCControlCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = VCControlView(bot)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # --- Create temp VC when user joins Make a Call ---
        if after.channel and after.channel.id == MAKE_A_CALL_ID:
            category = self.bot.get_channel(TEMP_CATEGORY_ID)
            if category:
                try:
                    # Create VC
                    new_vc = await member.guild.create_voice_channel(
                        f"{member.name}'s VC", category=category)
                    await new_vc.set_permissions(member, connect=True)

                    # Track ownership
                    self.view.owners[new_vc.id] = member.id

                    # Move member
                    await member.move_to(new_vc)

                    # Send control buttons to control panel channel
                    control_channel = self.bot.get_channel(CONTROL_PANEL_CHANNEL_ID)
                    if control_channel:
                        await control_channel.send(
                            content=f"{member.mention} here’s your VC control panel for **{new_vc.name}**:",
                            view=self.view
                        )

                except Exception as e:
                    print(f"Error creating temp VC: {e}")

        # --- Auto-delete empty VCs in the temp category ---
        if before.channel and before.channel.category_id == TEMP_CATEGORY_ID:
            if before.channel.id != MAKE_A_CALL_ID and len(before.channel.members) == 0:
                try:
                    await before.channel.delete(reason="Auto-deleted empty VC")
                except Exception as e:
                    print(f"Error deleting temp VC: {e}")

    @commands.command()
    async def send_vc_panel(self, ctx):
        """Manually send VC control panel (setup command)."""
        await ctx.send("VC Control Panel:", view=self.view)


async def setup(bot):
    await bot.add_cog(VCControlCog(bot))
