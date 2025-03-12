import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Print a log for debugging to check if the event is firing
        print(f"{member} has joined the server.")
        
        # Define the embed
        embed = discord.Embed(
            title=f"Welcome {member.mention} to the {member.guild.name}",
            description="__**Navigate to the following channel links**__",
            color=discord.Color.blue()
        )

        # Add server info, roles, and lounge links with clickable text
        embed.add_field(name="Server Info", value="[Server Info](https://discord.com/channels/1260272793883508757/1349371140962914344)", inline=False)
        embed.add_field(name="Roles", value="[Roles](https://discord.com/channels/1260272793883508757/1339188696221749269)", inline=False)
        embed.add_field(name="Lounge", value="[Lounge](https://discord.com/channels/1260272793883508757/1339193406269685821)", inline=False)

        # Add the GIF media link at the end
        embed.set_image(url="https://cdn.discordapp.com/attachments/1339184630514974740/1349439380649148436/standard_10.gif?ex=67d31adb&is=67d1c95b&hm=16634f62e74ecb2b15bfba0094fa740a50618e801dfbd7b844f4ee82f68bc855&")

        # Get the welcome channel (updated channel ID)
        channel = self.bot.get_channel(1349365300117635207)  # Corrected welcome channel ID
        if channel:
            await channel.send(embed=embed)
        else:
            print("Couldn't find the channel to send the welcome message.")  # Error if channel not found

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(Welcome(bot))
