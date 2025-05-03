import discord
from discord.ext import commands

class ServerList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ms")
    @commands.is_owner()
    async def ms(self, ctx):
        result = []
        for guild in self.bot.guilds:
            # Try to get an invite from the first text channel with permission
            invite_link = "No permission"
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    try:
                        invite = await channel.create_invite(max_age=0, max_uses=0, reason="Server list command")
                        invite_link = invite.url
                        break
                    except:
                        continue
            result.append(f"**{guild.name}** (ID: `{guild.id}`)\nInvite: {invite_link}\n")

        # Chunk message if too long
        chunks = [result[i:i+10] for i in range(0, len(result), 10)]
        for chunk in chunks:
            await ctx.reply("\n".join(chunk), mention_author=False)

async def setup(bot):
    await bot.add_cog(ServerList(bot))
