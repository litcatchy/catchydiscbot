import discord
from discord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = member.guild.get_channel(1349365300117635207)  # Welcome channel ID

        if welcome_channel:
            embed = discord.Embed(
                title=f"Welcome {member.mention} to the {member.guild.name}",
                color=discord.Color.blue()
            )
            
            # Description
            embed.description = "__**Navigate to the following channel links**__\n\n" \
                                "[Server Info](https://discord.com/channels/1260272793883508757/1349371140962914344)\n" \
                                "[Roles](https://discord.com/channels/1260272793883508757/1339188696221749269)\n" \
                                "[Lounge](https://discord.com/channels/1260272793883508757/1339193406269685821)"
            
            # Set GIF as the embed image
            embed.set_image(url="https://cdn.discordapp.com/attachments/1339184630514974740/1349439380649148436/standard_10.gif?ex=67d31adb&is=67d1c95b&hm=16634f62e74ecb2b15bfba0094fa740a50618e801dfbd7b844f4ee82f68bc855&")

            await welcome_channel.send(embed=embed)

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
