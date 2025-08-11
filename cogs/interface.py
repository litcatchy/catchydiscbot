import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput

# ===== MODALS =====
class RenameVCModal(Modal, title="Rename Voice Channel"):
    new_name = TextInput(label="New VC Name", placeholder="Enter a name", max_length=50)

    def __init__(self, vc):
        super().__init__()
        self.vc = vc

    async def on_submit(self, interaction: discord.Interaction):
        await self.vc.edit(name=self.new_name.value)
        await interaction.response.send_message(f"✅ Renamed VC to **{self.new_name.value}**", ephemeral=True)


class AddMemberModal(Modal, title="Add Member to VC"):
    member_id = TextInput(label="User ID", placeholder="Enter the user's ID")

    def __init__(self, vc):
        super().__init__()
        self.vc = vc

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.member_id.value))
            await self.vc.set_permissions(member, connect=True)
            await interaction.response.send_message(f"✅ Added {member.mention} to VC", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Could not add member. Make sure the ID is valid.", ephemeral=True)


class RemoveMemberModal(Modal, title="Remove Member from VC"):
    member_id = TextInput(label="User ID", placeholder="Enter the user's ID")

    def __init__(self, vc):
        super().__init__()
        self.vc = vc

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.member_id.value))
            await self.vc.set_permissions(member, overwrite=None)
            await interaction.response.send_message(f"✅ Removed {member.mention} from VC", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Could not remove member. Make sure the ID is valid.", ephemeral=True)


# ===== CONTROL PANEL =====
class VCControlView(View):
    def __init__(self, vc):
        super().__init__(timeout=None)
        self.vc = vc

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Allow only users in the VC to use the buttons
        if interaction.user in self.vc.members:
            return True
        await interaction.response.send_message("❌ You must be inside this VC to use these controls.", ephemeral=True)
        return False

    @discord.ui.button(label="Lock VC", style=discord.ButtonStyle.red)
    async def lock_vc(self, interaction: discord.Interaction, button: Button):
        await self.vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 VC locked.", ephemeral=True)

    @discord.ui.button(label="Unlock VC", style=discord.ButtonStyle.green)
    async def unlock_vc(self, interaction: discord.Interaction, button: Button):
        await self.vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 VC unlocked.", ephemeral=True)

    @discord.ui.button(label="Rename VC", style=discord.ButtonStyle.blurple)
    async def rename_vc(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RenameVCModal(self.vc))

    @discord.ui.button(label="Add Member", style=discord.ButtonStyle.gray)
    async def add_member(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(AddMemberModal(self.vc))

    @discord.ui.button(label="Remove Member", style=discord.ButtonStyle.gray)
    async def remove_member(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RemoveMemberModal(self.vc))


# ===== MAIN COG =====
class VoiceChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.make_a_call_id = 1401547369773793304  # Replace with your "Make a Call" VC ID
        self.temp_category_id = 1401547369773793302  # Replace with your Temp VC Category ID
        self.control_panel_channel_id = 1404367984168013854  # Replace with your control panel text channel ID

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # User joins "Make a Call" → Create Temp VC
        if after.channel and after.channel.id == self.make_a_call_id:
            category = self.bot.get_channel(self.temp_category_id)
            control_channel = self.bot.get_channel(self.control_panel_channel_id)

            if category and control_channel:
                new_vc = await member.guild.create_voice_channel(f"{member.name}'s VC", category=category)
                await new_vc.set_permissions(member, connect=True)

                await member.move_to(new_vc)

                # Send control panel
                await control_channel.send(
                    content=f"🎙️ {member.mention} created **{new_vc.name}** — VC controls below:",
                    view=VCControlView(new_vc)
                )

        # Auto-delete empty temp VCs (except Make a Call)
        if before.channel and before.channel.category_id == self.temp_category_id:
            if before.channel.id != self.make_a_call_id and len(before.channel.members) == 0:
                await before.channel.delete(reason="Auto-deleted empty VC")


# ===== SETUP =====
async def setup(bot):
    await bot.add_cog(VoiceChannelManager(bot))
