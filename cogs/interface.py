import discord
from discord.ext import commands, tasks
import asyncio

class VCControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

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
        if vc.members and vc.members[0] != interaction.user:  
            await vc.edit(name=f"{interaction.user.name}'s VC")  
            await interaction.response.send_message("You claimed the voice channel.", ephemeral=True)  
        else:  
            await interaction.response.send_message("You're already the first member in this VC.", ephemeral=True)  

    @discord.ui.button(label="Transfer", style=discord.ButtonStyle.secondary, custom_id="vc_transfer")  
    async def transfer_vc(self, interaction: discord.Interaction, button: discord.ui.Button):  
        vc = interaction.user.voice.channel
        if vc.owner != interaction.user:
            await interaction.response.send_message("You must be the owner of the voice channel to transfer ownership.", ephemeral=True)
            return

        # List members in the VC
        members = [member.name for member in vc.members]
        options = [discord.SelectOption(label=member, value=member) for member in members]

        select = discord.ui.Select(
            placeholder="Choose a person to transfer ownership",
            options=options,
            custom_id="transfer_select"
        )

        async def transfer_callback(interaction: discord.Interaction):
            new_owner = interaction.data['values'][0]
            member = discord.utils.get(vc.members, name=new_owner)
            await vc.edit(owner=member)
            await interaction.response.send_message(f"Ownership of the VC has been transferred to {new_owner}.", ephemeral=True)

        select.callback = transfer_callback
        await interaction.response.send_message("Please select who to transfer ownership to.", ephemeral=True, view=discord.ui.View(select))

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, custom_id="vc_disconnect")  
    async def disconnect_member(self, interaction: discord.Interaction, button: discord.ui.Button):  
        vc = interaction.user.voice.channel  
        if vc.owner != interaction.user:
            await interaction.response.send_message("You must be the owner of the voice channel to disconnect a member.", ephemeral=True)
            return

        # List members in the VC
        members = [member.name for member in vc.members]
        options = [discord.SelectOption(label=member, value=member) for member in members]

        select = discord.ui.Select(
            placeholder="Choose a person to disconnect",
            options=options,
            custom_id="disconnect_select"
        )

        async def disconnect_callback(interaction: discord.Interaction):
            member_name = interaction.data['values'][0]
            member = discord.utils.get(vc.members, name=member_name)
            await member.move_to(None)  # Disconnect the member
            await interaction.response.send_message(f"{member_name} has been disconnected from the VC.", ephemeral=True)

        select.callback = disconnect_callback
        await interaction.response.send_message("Please select who to disconnect from the VC.", ephemeral=True, view=discord.ui.View(select))

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.secondary, custom_id="vc_delete")  
    async def delete_vc(self, interaction: discord.Interaction, button: discord.ui.Button):  
        vc = interaction.user.voice.channel  
        if vc.id != 1364639518279467079:  # Avoid deleting the specific VC  
            await vc.delete(reason=f"Deleted by {interaction.user}")  
            await interaction.response.send_message("Voice channel deleted.", ephemeral=True)  
        else:  
            await interaction.response.send_message("This voice channel cannot be deleted.", ephemeral=True)

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
Delete - Delete your voice channel""",
            color=discord.Color.blurple()
        )
        view = VCControlView(self.bot)
        self.panel_message = await channel.send(embed=embed, view=view)

    @send_panel.before_loop  
    async def before_panel(self):  
        await self.bot.wait_until_ready()  

    @commands.Cog.listener()  
    async def on_voice_state_update(self, member, before, after):  
        if after.channel and after.channel.id == 1364639518279467079:  # Check if user joins the special channel  
            category = self.bot.get_channel(1359208824497639424)  
            if category:  
                new_vc = await member.guild.create_voice_channel(  
                    f"{member.name}'s VC", category=category)  
                await new_vc.set_permissions(member, connect=True)  
                await member.move_to(new_vc)  
                await self.send_panel()  # Ensure panel is refreshed  
                await self.delete_inactive_vc(new_vc)  

    async def delete_inactive_vc(self, vc):  
        await asyncio.sleep(600)  # 10 minutes  
        if len(vc.members) == 0:  
            await vc.delete()

async def setup(bot):
    await bot.add_cog(VCControl(bot))
