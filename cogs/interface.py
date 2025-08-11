import discord
from discord.ext import commands
from discord.ui import View, button
import asyncio

# ===== CONFIG =====
MAKE_A_CALL_ID = 1401547369773793304       # "Make a Call" channel (users join this to create a temp VC)
TEMP_CATEGORY_ID = 1401547369773793302     # Category where temp VCs will be created
CONTROL_PANEL_CHANNEL_ID = 1404367984168013854  # Text channel where the bot pings users & posts control messages

# ===== VIEW =====
class VCControlView(View):
    def __init__(self, bot: commands.Bot, vc_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.vc_id = vc_id  # controls are tied to a specific VC id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ensure the clicking user is currently inside the VC this view was created for
        try:
            member_voice = interaction.user.voice
            if not member_voice or not member_voice.channel:
                await interaction.response.send_message("❌ You must be in the voice channel to use these controls.", ephemeral=True)
                return False
            if member_voice.channel.id != self.vc_id:
                await interaction.response.send_message("❌ These controls are for a different VC.", ephemeral=True)
                return False
            return True
        except Exception:
            await interaction.response.send_message("❌ Unable to verify your voice status.", ephemeral=True)
            return False

    @button(label="🔒 Lock", style=discord.ButtonStyle.danger, custom_id="vc_lock")
    async def lock_button(self, interaction: discord.Interaction, btn: discord.ui.Button):
        vc = self.bot.get_channel(self.vc_id)
        if not isinstance(vc, discord.VoiceChannel):
            return await interaction.response.send_message("❌ Voice channel not found.", ephemeral=True)
        try:
            await vc.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.response.send_message("🔒 Voice channel locked (no new connects).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to lock VC: {e}", ephemeral=True)

    @button(label="🔓 Unlock", style=discord.ButtonStyle.success, custom_id="vc_unlock")
    async def unlock_button(self, interaction: discord.Interaction, btn: discord.ui.Button):
        vc = self.bot.get_channel(self.vc_id)
        if not isinstance(vc, discord.VoiceChannel):
            return await interaction.response.send_message("❌ Voice channel not found.", ephemeral=True)
        try:
            await vc.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.response.send_message("🔓 Voice channel unlocked.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unlock VC: {e}", ephemeral=True)

    @button(label="➕ Add Slot", style=discord.ButtonStyle.secondary, custom_id="vc_add_slot")
    async def add_slot_button(self, interaction: discord.Interaction, btn: discord.ui.Button):
        vc = self.bot.get_channel(self.vc_id)
        if not isinstance(vc, discord.VoiceChannel):
            return await interaction.response.send_message("❌ Voice channel not found.", ephemeral=True)
        try:
            current = vc.user_limit if vc.user_limit is not None and vc.user_limit != 0 else len(vc.members)
            new_limit = current + 1
            # If new_limit == 0 it means unlimited, but new_limit >0 here
            await vc.edit(user_limit=new_limit)
            await interaction.response.send_message(f"✅ VC user limit increased to **{new_limit}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to increase limit: {e}", ephemeral=True)

    @button(label="➖ Remove Slot", style=discord.ButtonStyle.secondary, custom_id="vc_remove_slot")
    async def remove_slot_button(self, interaction: discord.Interaction, btn: discord.ui.Button):
        vc = self.bot.get_channel(self.vc_id)
        if not isinstance(vc, discord.VoiceChannel):
            return await interaction.response.send_message("❌ Voice channel not found.", ephemeral=True)
        try:
            current = vc.user_limit if vc.user_limit is not None and vc.user_limit != 0 else len(vc.members)
            new_limit = current - 1
            # Discord treats 0 as unlimited — user asked "down to 0 = unlimited"
            if new_limit <= 0:
                await vc.edit(user_limit=0)
                await interaction.response.send_message("✅ VC user limit set to **unlimited** (0).", ephemeral=True)
            else:
                await vc.edit(user_limit=new_limit)
                await interaction.response.send_message(f"✅ VC user limit decreased to **{new_limit}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to decrease limit: {e}", ephemeral=True)


# ===== COG =====
class VoiceChannelManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Mapping: vc_id -> list of control message ids posted in control channel for cleanup
        self._vc_control_messages: dict[int, list[int]] = {}
        # Ensure the bot will keep views alive across restarts if desired (optional)
        # Not registering persistent view here; views are attached to sent messages.
        bot.loop.create_task(self._wait_ready_and_register_cleanup())

    async def _wait_ready_and_register_cleanup(self):
        await self.bot.wait_until_ready()
        # nothing needed currently, placeholder for future persistent view registration
        return

    async def _send_control_message_for_member(self, guild: discord.Guild, vc: discord.VoiceChannel, member: discord.Member):
        """
        Send a control message in the control panel channel pinging `member` and attaching a VCControlView
        The message is visible to everyone in the control channel, but interactions will be ephemeral when clicked
        and are gated so only members inside `vc` can use them.
        """
        control_chan = self.bot.get_channel(CONTROL_PANEL_CHANNEL_ID)
        if control_chan is None:
            return None

        view = VCControlView(self.bot, vc.id)
        try:
            # Ping the specific member; message itself is visible publicly, but only that member (or others in VC)
            # can use the controls because interaction_check verifies their voice channel.
            msg = await control_chan.send(content=f"{member.mention} • Controls for **{vc.name}** — click the buttons below (ephemeral responses).", view=view)
            # Track message for cleanup when VC is deleted
            self._vc_control_messages.setdefault(vc.id, []).append(msg.id)
            return msg
        except Exception:
            return None

    async def _send_controls_to_vc_members(self, guild: discord.Guild, vc: discord.VoiceChannel):
        # Send a control message in the control panel channel for every member currently in the VC
        for m in vc.members:
            # small throttle to avoid rate limits if many members join at once
            await self._send_control_message_for_member(guild, vc, m)
            await asyncio.sleep(0.15)

    async def _cleanup_control_messages_for_vc(self, guild: discord.Guild, vc_id: int):
        """Delete tracked control messages for a VC to keep control channel clean."""
        control_chan = self.bot.get_channel(CONTROL_PANEL_CHANNEL_ID)
        if control_chan is None:
            return
        msg_ids = self._vc_control_messages.pop(vc_id, [])
        for mid in msg_ids:
            try:
                msg = await control_chan.fetch_message(mid)
                await msg.delete()
                await asyncio.sleep(0.05)
            except Exception:
                # ignore fetch/delete errors
                pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # --- User joined the "Make a Call" VC: create personal temp VC and move them ---
        try:
            if after and after.channel and after.channel.id == MAKE_A_CALL_ID:
                guild = member.guild
                category = guild.get_channel(TEMP_CATEGORY_ID)
                if category and isinstance(category, discord.CategoryChannel):
                    try:
                        new_vc = await guild.create_voice_channel(name=f"{member.name}'s VC", category=category)
                        # Allow the member to connect explicitly (helps in some setups)
                        await new_vc.set_permissions(member, connect=True)
                        # Move them into the new vc
                        await member.move_to(new_vc)
                        # Send ephemeral-capable control messages for each member currently in the vc (initially just the creator)
                        await self._send_controls_to_vc_members(guild, new_vc)
                    except Exception:
                        # creation/move might fail silently if permissions missing
                        return
        except Exception:
            pass

        # --- When a user joins a temp VC (not necessarily created right now), send them their control msg ---
        try:
            # if they moved into a voice channel that belongs to the temp category (but isn't Make a Call)
            if after and after.channel and after.channel.category_id == TEMP_CATEGORY_ID and after.channel.id != MAKE_A_CALL_ID:
                vc = after.channel
                # send controls for the joining member only
                await self._send_control_message_for_member(vc.guild, vc, member)

                # Also, if this VC didn't have control messages tracked yet, ensure others have controls too
                if vc.id not in self._vc_control_messages:
                    # send controls for all existing members to ensure each has a message
                    await self._send_controls_to_vc_members(vc.guild, vc)
        except Exception:
            pass

        # --- Auto-delete empty temp VCs (except Make a Call) and cleanup control messages ---
        try:
            if before and before.channel and before.channel.category_id == TEMP_CATEGORY_ID and before.channel.id != MAKE_A_CALL_ID:
                vc = before.channel
                # If channel is now empty, delete it and cleanup control messages
                if len(vc.members) == 0:
                    try:
                        await self._cleanup_control_messages_for_vc(vc.guild, vc.id)
                        await vc.delete(reason="Auto-deleted empty temp VC")
                    except Exception:
                        # ignore deletion errors
                        pass
        except Exception:
            pass

    # Optional command to manually send panel (for admins)
    @commands.command(name="vcpanel")
    @commands.has_permissions(manage_channels=True)
    async def vcpanel(self, ctx: commands.Context):
        """(Admin) Send a note about VC controls to the control panel channel."""
        control_chan = self.bot.get_channel(CONTROL_PANEL_CHANNEL_ID)
        if control_chan:
            await control_chan.send("💠 VC Controls: Join the Make-a-Call voice channel to create a temporary VC and get controls (ephemeral responses on button clicks).")
            await ctx.send("Sent.", delete_after=5)
        else:
            await ctx.send("Control channel not found.", delete_after=5)


# ===== SETUP =====
async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceChannelManager(bot))
