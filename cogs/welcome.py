import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_welcome_message(member)

    @commands.command(name="welcum")
    async def test_welcome(self, ctx):
        await self.send_welcome_message(ctx.author)

    async def send_welcome_message(self, member):
        channel = member.guild.get_channel(1339193406269685821)
        if channel is None:
            return

        embed = discord.Embed(
            description=f"Welcome {member.mention} to {member.guild.name}\n– say something! we don’t bite (:",
            color=discord.Color.blurple()
        )

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="👤 Edit Profile Roles", url="https://discord.com/channels/1260272793883508757/1339188696221749269"))
        view.add_item(discord.ui.Button(label="ℹ️ Server info", url="https://discord.com/channels/1260272793883508757/1337115224217751622"))

        message = await channel.send(content=member.mention, embed=embed, view=view)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=10))
        await message.delete()

async def setup(bot):
    await bot.add_cog(Welcome(bot))
