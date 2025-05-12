import discord
from discord.ext import commands
import re
from datetime import datetime

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_role_id = 1371429530673348648
        self.log_channel_id = 1339898523407355945
        self.invite_pattern = re.compile(
            r"(d\s*i\s*s\s*c\s*o\s*r\s*d\s*(\.\s*g\s*g|\.\s*c\s*o\s*m)?\s*(/|\.\s*|\s)*[a-zA-Z0-9]+|discordapp\s*\.\s*com\s*/\s*invite\s*/[a-zA-Z0-9]+|discord\s*\.\s*gift\s*/[a-zA-Z0-9]+|\.\s*gg\s*/[a-zA-Z0-9]+)",
            re.IGNORECASE
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Normalize message by removing spaces and lowering case
        normalized = re.sub(r"\s+", "", message.content.lower())

        if self.invite_pattern.search(normalized):
            # Check if user has the allowed role
            if not any(role.id == self.link_role_id for role in message.author.roles):
                try:
                    await message.delete()
                except discord.Forbidden:
                    return

                warning = discord.Embed(
                    description="Only people with the `link` role are allowed to send links",
                    color=discord.Color.purple()
                )
                await message.channel.send(embed=warning, delete_after=5)

                log_channel = self.bot.get_channel(self.log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="Deleted Invite Message",
                        color=discord.Color.purple(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="User", value=f"{message.author.mention} ({message.author.id})", inline=False)
                    embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                    embed.add_field(name="Message", value=discord.utils.escape_markdown(message.content)[:1024], inline=False)
                    embed.set_footer(text="Invite blocked", icon_url=message.author.display_avatar.url)

                    await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LinkFilter(bot))
  
