import discord
from discord.ext import commands

GENDER_ROLE_IDS = {
    "Male": 1371163384816603188,
    "Female": 1371163401736425578
}

GENDER_EMOJIS = {
    "Male": discord.Object(id=1359446626736803921),
    "Female": discord.Object(id=1359446610391863316)
}

AUTO_ROLE_ID = 1361487173525831771
WELCOME_CHANNEL_ID = 1339193406269685821

class GenderDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Male",
                description="Get the Male role",
                emoji=GENDER_EMOJIS["Male"]
            ),
            discord.SelectOption(
                label="Female",
                description="Get the Female role",
                emoji=GENDER_EMOJIS["Female"]
            )
        ]
        super().__init__(placeholder="Select your gender", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        role_id = GENDER_ROLE_IDS[selected]
        role = interaction.guild.get_role(role_id)

        if role:
            # Remove the other gender role if already assigned
            other_role_id = [rid for name, rid in GENDER_ROLE_IDS.items() if name != selected][0]
            other_role = interaction.guild.get_role(other_role_id)
            if other_role in interaction.user.roles:
                await interaction.user.remove_roles(other_role)

            if role not in interaction.user.roles:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"You've been given the **{selected}** role.", ephemeral=True)
            else:
                await interaction.response.send_message(f"You already have the **{selected}** role.", ephemeral=True)
        else:
            await interaction.response.send_message("Something went wrong with assigning the role.", ephemeral=True)

class GenderDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GenderDropdown())

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Auto-role assign
        auto_role = member.guild.get_role(AUTO_ROLE_ID)
        if auto_role:
            await member.add_roles(auto_role)

        # Send welcome message
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                description=f"welcome {member.mention}, say something! we don’t bite (:",
                color=discord.Color.random()
            )
            await channel.send(embed=embed, view=GenderDropdownView())

async def setup(bot):
    await bot.add_cog(Welcome(bot))
