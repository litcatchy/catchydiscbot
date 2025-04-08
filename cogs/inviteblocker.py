import discord
from discord.ext import commands

class InviteBlocker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.attempts = {}

    async def process_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.author, discord.User):
            return  # Skip if it's not a guild member

        if message.guild is None:
            return

        # Exemptions
        if message.author.id == message.guild.owner_id:
            return
        if message.author.guild_permissions.administrator:
            return

        # Invite patterns
        invite_patterns = [
            "discord.gg/",
            "discord.com/invite/",
            ".gg/",
            "gg."
        ]

        if any(pattern in message.content.lower() for pattern in invite_patterns):
            try:
                await message.delete()
            except discord.NotFound:
                pass  # Message already deleted

            # Increment attempts
            user_attempts = self.attempts.get(message.author.id, 0) + 1
            self.attempts[message.author.id] = user_attempts

            # Send warning embed
            warning_embed = discord.Embed(
                description=f"{message.author.mention}, sending server invite links is strictly prohibited.",
                color=discord.Color.red()
            )
            try:
                await message.channel.send(embed=warning_embed)
            except discord.Forbidden:
                pass  # No permission to send in the channel

            # Log embed
            log_channel = self.bot.get_channel(1339898523407355945)
            if log_channel:
                log_embed = discord.Embed(
                    title="Invite Link Detected",
                    color=discord.Color.red()
                )
                log_embed.add_field(name="User", value=f"{message.author} (`{message.author.id}`)", inline=False)
                log_embed.add_field(name="Channel", value=f"{message.channel.mention} (`{message.channel.id}`)", inline=False)
                log_embed.add_field(name="Message Content", value=message.content, inline=False)
                log_embed.add_field(name="Attempt Count", value=str(user_attempts), inline=False)
                log_embed.set_footer(text="Invite Blocker Log")
                log_embed.timestamp = discord.utils.utcnow()

                try:
                    await log_channel.send(embed=log_embed)
                except discord.Forbidden:
                    pass  # No permission to send log

            # Timeout after 3 attempts
            if user_attempts >= 3:
                try:
                    await message.author.timeout(duration=600, reason="Exceeded invite link attempts")
                    # Log timeout
                    if log_channel:
                        timeout_embed = discord.Embed(
                            title="User Timed Out",
                            description=f"{message.author.mention} has been timed out for 10 minutes due to repeated invite links.",
                            color=discord.Color.dark_red()
                        )
                        timeout_embed.add_field(name="User", value=f"{message.author} (`{message.author.id}`)", inline=False)
                        timeout_embed.add_field(name="Reason", value="Exceeded invite link attempts", inline=False)
                        timeout_embed.set_footer(text="Invite Blocker Log")
                        timeout_embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=timeout_embed)
                except Exception as e:
                    if log_channel:
                        error_embed = discord.Embed(
                            title="Timeout Error",
                            description=f"Failed to timeout {message.author.mention}.\nError: {e}",
                            color=discord.Color.orange()
                        )
                        error_embed.set_footer(text="Invite Blocker Log")
                        error_embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=error_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.process_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.process_message(after)

async def setup(bot):
    await bot.add_cog(InviteBlocker(bot))
