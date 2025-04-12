import discord
from discord.ext import commands, tasks
import datetime

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_ping_tracker = {}  # {user_id: [timestamps]}
        self.webhook_ping_tracker = {}  # {webhook_id: [timestamps]}
        self.cleanup_old_pings.start()

    @tasks.loop(minutes=30)
    async def cleanup_old_pings(self):
        now = datetime.datetime.utcnow()
        six_hours_ago = now - datetime.timedelta(hours=6)

        self.user_ping_tracker = {
            uid: [t for t in times if t > six_hours_ago]
            for uid, times in self.user_ping_tracker.items()
        }

        self.webhook_ping_tracker = {
            wid: [t for t in times if t > six_hours_ago]
            for wid, times in self.webhook_ping_tracker.items()
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return

        # Corrected here
        if not message.mention_everyone:
            return

        now = datetime.datetime.utcnow()

        # Webhook Handling
        if isinstance(message.webhook_id, int):
            webhook_id = message.webhook_id
            self.webhook_ping_tracker.setdefault(webhook_id, []).append(now)

            pings = self.webhook_ping_tracker[webhook_id]
            recent_pings = [t for t in pings if (now - t).total_seconds() <= 21600]

            if len(recent_pings) == 1:
                warning_embed = discord.Embed(
                    title="Webhook Ping Warning",
                    description="A webhook just pinged `@everyone` or `@here`. One ping is allowed every 6 hours.",
                    color=discord.Color.orange()
                )
                warning_embed.set_footer(text="1/1 ping in the last 6 hours already done")
                try:
                    await message.channel.send(embed=warning_embed)
                except discord.Forbidden:
                    pass

            elif len(recent_pings) > 1:
                try:
                    webhooks = await message.channel.webhooks()
                    for wh in webhooks:
                        if wh.id == webhook_id:
                            await wh.delete()
                            deleted_embed = discord.Embed(
                                title="Webhook Deleted",
                                description="A webhook was deleted for spamming `@everyone` or `@here` more than once in 6 hours.",
                                color=discord.Color.red()
                            )
                            await message.channel.send(embed=deleted_embed)
                            break
                except discord.Forbidden:
                    pass
                except Exception:
                    pass

        else:
            user = message.author
            if user.id == message.guild.owner_id:
                return

            self.user_ping_tracker.setdefault(user.id, []).append(now)

            pings = self.user_ping_tracker[user.id]
            recent_pings = [t for t in pings if (now - t).total_seconds() <= 21600]

            if len(recent_pings) == 1:
                try:
                    warning_embed = discord.Embed(
                        title="Warning",
                        description=f"{user.mention} you’re only allowed to ping `@everyone` or `@here` once every 6 hours, next ping within that time will result in role removal.",
                        color=discord.Color.orange()
                    )
                    warning_embed.set_footer(text="1/1 ping in the last 6 hours already done")
                    await message.channel.send(embed=warning_embed)
                except discord.Forbidden:
                    pass

            elif len(recent_pings) > 1:
                try:
                    roles_to_remove = [role for role in user.roles if role != message.guild.default_role]
                    if roles_to_remove:
                        await user.remove_roles(*roles_to_remove, reason="Exceeded ping limit")
                except discord.Forbidden:
                    pass
                except Exception:
                    pass

                try:
                    alert_embed = discord.Embed(
                        title="Roles Removed",
                        description=f"{user.mention} pinged `@everyone` or `@here` more than once in 6 hours. All roles removed.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=alert_embed)
                except discord.Forbidden:
                    pass

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
