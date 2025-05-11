import discord
from discord.ext import commands

class WelcomeDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select your gender",
        options=[
            discord.SelectOption(label="Male", value="1371163384816603188", emoji="<:male:1359446626736803921>"),
            discord.SelectOption(label="Female", value="1371163401736425578", emoji="<:female:1359446610391863316>"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        role_id = int(select.values[0])
        role = interaction.guild.get_role(role_id)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Role `{role.name}` has been assigned!", ephemeral=True)
        else:
            await interaction.response.send_message("That role could not be found.", ephemeral=True)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Assign default role
        default_role = member.guild.get_role(1361487173525831771)
        if default_role:
            await member.add_roles(default_role)

        # Get welcome channel
        channel = member.guild.get_channel(1339193406269685821)
        if channel:
            # Ping the user outside the embed
            await channel.send(member.mention)

            # Send the embed with the user mention
            embed = discord.Embed(
                description=f"{member.mention} welcome to {member.guild.name}, say something! We don’t bite (:",
                color=discord.Color.blurple()
            )
            view = WelcomeDropdown()
            await channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
