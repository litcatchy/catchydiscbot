import discord
from discord.ext import commands
from discord.utils import format_dt
from datetime import datetime
import pytz

TRIGGER_EMOJIS = {"💀", "☠️", "😭", "⭐"}
THRESHOLD = 3
STARBOARD_CHANNEL_ID = 1371523168241455124

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = {}  # {original_msg_id: starboard_msg_id}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.handle_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.handle_reaction(payload)

    async def handle_reaction(self, payload):
        if str(payload.emoji.name) not in TRIGGER_EMOJIS:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        if message.author.bot:
            return

        emoji_used = None
        emoji_count = 0

        for reaction in message.reactions:
            if str(reaction.emoji) in TRIGGER_EMOJIS and reaction.count >= THRESHOLD:
                emoji_used = str(reaction.emoji)
                emoji_count = reaction.count
                break

        starboard_channel = self.bot.get_channel(STARBOARD_CHANNEL_ID)
        if not starboard_channel:
            return

        # Post to starboard
        if emoji_used and message.id not in self.message_cache:
            embed = discord.Embed(
                description=message.content if message.content else "*No text content*",
                color=discord.Color.purple()
            )

            embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)

            # Add reply content if present
            if message.reference:
                try:
                    replied = await channel.fetch_message(message.reference.message_id)
                    reply_text = replied.content or "*[No text]*"
                    embed.add_field(
                        name=f"Replied to {replied.author.name}",
                        value=reply_text,
                        inline=False
                    )
                except:
                    pass

            # Add image if present
            for a in message.attachments:
                if a.content_type and a.content_type.startswith("image"):
                    embed.set_image(url=a.url)
                    break

            # Set footer with current time in Asia/Kolkata
            india_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p • %d %b %Y")
            embed.set_footer(text=f"{india_time}")

            # Jump button
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="Go to the message",
                url=message.jump_url,
                style=discord.ButtonStyle.link
            ))

            header = f"{emoji_used} **{emoji_count} |** <#{channel.id}> **(**<@{message.author.id}>**)**"

            sent_msg = await starboard_channel.send(content=header, embed=embed, view=view)
            self.message_cache[message.id] = sent_msg.id

        # Remove from starboard if reaction count drops below threshold
        elif message.id in self.message_cache and not emoji_used:
            try:
                sb_msg_id = self.message_cache[message.id]
                sb_msg = await starboard_channel.fetch_message(sb_msg_id)
                await sb_msg.delete()
                del self.message_cache[message.id]
            except:
                pass

async def setup(bot):
    await bot.add_cog(Starboard(bot))
