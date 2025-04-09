import discord from discord.ext import commands from discord import ui, Interaction, Embed

CHANNEL_ID = 1339188696221749269 GUILD_ID = 1260272793883508757

ROLE_IDS = { "male": 1339877108347961386, "female": 1339877064999960606, "adult": 1339877455196061742, "minor": 1339877409846988830, "edate": 1359438372245995600, "polls": 1359438345679142932, "vc": 1359438394429542480, "chat_reviver": 1359438442525884476, }

EMOJIS = { "male": "<:male:1359446626736803921>", "female": "<:female:1359446610391863316>", "adult": "<:adult:1359446704423702619>", "minor": "<:minor:1359446770966331392>", "edate": "<:edate:1359446814000156842>", "polls": "<:polls:1359446860229513256>", "vc": "📢", "chat_reviver": "<:chatreviver:1359438442525884476>", }

current_panel_message = None

class SelfRoleView(ui.View): def init(self): super().init(timeout=None) self.add_item(GenderDropdown()) self.add_item(AgeDropdown()) self.add_item(ActivityDropdown())

class GenderDropdown(ui.Select): def init(self): options = [ discord.SelectOption(label="Female", value="female", emoji=EMOJIS["female"]), discord.SelectOption(label="Male", value="male", emoji=EMOJIS["male"]), ] super().init(placeholder=",gender", min_values=1, max_values=1, options=options)

async def callback(self, interaction: Interaction):
    await handle_role_selection(interaction, self.values[0], category="gender")

class AgeDropdown(ui.Select): def init(self): options = [ discord.SelectOption(label="Adult", value="adult", emoji=EMOJIS["adult"]), discord.SelectOption(label="Minor", value="minor", emoji=EMOJIS["minor"]), ] super().init(placeholder=",age", min_values=1, max_values=1, options=options)

async def callback(self, interaction: Interaction):
    await handle_role_selection(interaction, self.values[0], category="age")

class ActivityDropdown(ui.Select): def init(self): options = [ discord.SelectOption(label="E-Date", value="edate", emoji=EMOJIS["edate"]), discord.SelectOption(label="Polls", value="polls", emoji=EMOJIS["polls"]), discord.SelectOption(label="VC", value="vc", emoji=EMOJIS["vc"]), discord.SelectOption(label="Chat Reviver", value="chat_reviver", emoji=EMOJIS["chat_reviver"]), ] super().init(placeholder=",activity", min_values=1, max_values=len(options), options=options)

async def callback(self, interaction: Interaction):
    for value in self.values:
        await handle_role_selection(interaction, value, category="activity", ephemeral=False)
    await interaction.response.send_message("Your selected roles have been updated.", ephemeral=True)

async def handle_role_selection(interaction: Interaction, selected_value: str, category: str = None, ephemeral: bool = True): member = interaction.user guild = interaction.guild role = guild.get_role(ROLE_IDS[selected_value])

if category in ["gender", "age"]:
    category_roles = {
        k: v for k, v in ROLE_IDS.items() if (category == "gender" and k in ("male", "female")) or (category == "age" and k in ("adult", "minor"))
    }
    for role_name, role_id in category_roles.items():
        existing_role = guild.get_role(role_id)
        if existing_role in member.roles and existing_role != role:
            await member.remove_roles(existing_role)

if role in member.roles:
    await member.remove_roles(role)
    response = f"[`{role.name}`] has been successfully removed."
else:
    await member.add_roles(role)
    response = f"[`{role.name}`] has been assigned."

if ephemeral:
    await interaction.response.send_message(response, ephemeral=True)
else:
    await interaction.followup.send(response, ephemeral=True)

class SelfRoles(commands.Cog): def init(self, bot): self.bot = bot self.panel_task.start()

def cog_unload(self):
    self.panel_task.cancel()

@tasks.loop(count=1)
async def panel_task(self):
    global current_panel_message
    await self.bot.wait_until_ready()
    channel = self.bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    try:
        history = [message async for message in channel.history(limit=10)]
        for message in history:
            if message.author == self.bot.user and message.components:
                await message.delete()
    except Exception:
        pass

    embed = Embed(title="Self Roles Panel", description="Select your roles below:", color=discord.Color.blurple())
    embed.add_field(name="Gender", value=f"{EMOJIS['female']} Female\n{EMOJIS['male']} Male", inline=False)
    embed.add_field(name="Age", value=f"{EMOJIS['adult']} Adult\n{EMOJIS['minor']} Minor", inline=False)
    embed.add_field(name="Activity", value=f"{EMOJIS['edate']} E-Date\n{EMOJIS['polls']} Polls\n{EMOJIS['vc']} VC\n{EMOJIS['chat_reviver']} Chat Reviver", inline=False)
    embed.set_footer(text="Select your roles from the dropdowns below!")

    current_panel_message = await channel.send(embed=embed, view=SelfRoleView())

async def setup(bot): await bot.add_cog(SelfRoles(bot))

