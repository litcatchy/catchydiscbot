import discord
from discord.ext import commands, tasks

class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.panel_message = None
        self.self_roles_channel_id = 1339188696221749269
        self.gender_roles = {
            "male": 1339877108347961386,
            "female": 1339877064999960606
        }
        self.age_roles = {
            "adult": 1339877455196061742,
            "minor": 1339877409846988830
        }
        self.activity_roles = {
            "edate": 1359438372245995600,
            "polls": 1359438345679142932,
            "vc": 1359438394429542480,
            "chatreviver": 1359438442525884476
        }
        self.bot.loop.create_task(self.setup_panel())

    async def setup_panel(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.self_roles_channel_id)
        if channel is None:
            print(f"Channel with ID {self.self_roles_channel_id} not found.")
            return

        async for msg in channel.history(limit=10):
            if msg.author == self.bot.user:
                await msg.delete()

        embed = discord.Embed(
            title="Self Roles Panel",
            description="Select your roles from the menus below!",
            color=discord.Color.blurple()
        )

        view = SelfRoleView(self)
        self.panel_message = await channel.send(embed=embed, view=view)

    async def assign_role(self, interaction: discord.Interaction, role: discord.Role):
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f"Removed role: `{role.name}`", ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"Assigned role: `{role.name}`", ephemeral=True
            )

class SelfRoleView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.add_item(GenderSelect(cog))
        self.add_item(AgeSelect(cog))
        self.add_item(ActivitySelect(cog))

class GenderSelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        options = [
            discord.SelectOption(label="Female", value="female", emoji="<:female:1359446610391863316>"),
            discord.SelectOption(label="Male", value="male", emoji="<:male:1359446626736803921>")
        ]
        super().__init__(placeholder="，gender", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        role_id = self.cog.gender_roles[self.values[0]]
        role = interaction.guild.get_role(role_id)

        # Remove other gender role if present
        for gender_role_id in self.cog.gender_roles.values():
            r = interaction.guild.get_role(gender_role_id)
            if r in interaction.user.roles and r != role:
                await interaction.user.remove_roles(r)

        await self.cog.assign_role(interaction, role)

class AgeSelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        options = [
            discord.SelectOption(label="Adult", value="adult", emoji="<:adult:1359446704423702619>"),
            discord.SelectOption(label="Minor", value="minor", emoji="<:minor:1359446770966331392>")
        ]
        super().__init__(placeholder="，age", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        role_id = self.cog.age_roles[self.values[0]]
        role = interaction.guild.get_role(role_id)

        # Remove other age role if present
        for age_role_id in self.cog.age_roles.values():
            r = interaction.guild.get_role(age_role_id)
            if r in interaction.user.roles and r != role:
                await interaction.user.remove_roles(r)

        await self.cog.assign_role(interaction, role)

class ActivitySelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        options = [
            discord.SelectOption(label="Edate", value="edate", emoji="<:edate:1359446814000156842>"),
            discord.SelectOption(label="Polls", value="polls", emoji="<:polls:1359446860229513256>"),
            discord.SelectOption(label="VC", value="vc", emoji="📢"),
            discord.SelectOption(label="Chat Reviver", value="chatreviver", emoji="<:chatreviver:1359448891983921272>")
        ]
        super().__init__(placeholder="，activity", min_values=1, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        roles_to_add = []
        roles_to_remove = []

        selected_role_ids = {self.cog.activity_roles[v] for v in self.values}
        user_role_ids = {role.id for role in interaction.user.roles}

        for value, role_id in self.cog.activity_roles.items():
            role = interaction.guild.get_role(role_id)
            if role_id in selected_role_ids:
                if role_id not in user_role_ids:
                    roles_to_add.append(role)
            else:
                if role_id in user_role_ids:
                    roles_to_remove.append(role)

        if roles_to_add:
            await interaction.user.add_roles(*roles_to_add)

        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)

        messages = []
        for role in roles_to_add:
            messages.append(f"Assigned role: `{role.name}`")
        for role in roles_to_remove:
            messages.append(f"Removed role: `{role.name}`")

        if not messages:
            messages.append("No changes were made.")

        await interaction.response.send_message("\n".join(messages), ephemeral=True)

async def setup(bot):
    await bot.add_cog(SelfRoles(bot))
