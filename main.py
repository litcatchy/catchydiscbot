import discord
from discord.ext import commands
import os
import asyncio

# Set up intents to allow the bot to access member data and message content
intents = discord.Intents.default()
intents.members = True  # For member-related events (e.g., member join, leave)
intents.message_content = True  # For accessing message content

# Create the bot instance with the command prefix and the updated intents
bot = commands.Bot(command_prefix=",", intents=intents)

# Function to load cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

# Define the setup_hook method to load cogs and sync commands
async def setup_hook():
    await load_cogs()
    try:
        await bot.tree.sync()
        print("Synced application commands (slash commands).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.setup_hook = setup_hook

# Event to notify when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Command to load a cog
@bot.command()
async def load(ctx, extension):
    """Load a cog dynamically."""
    try:
        await bot.load_extension(f"cogs.{extension}")
        await bot.tree.sync()
        await ctx.send(f"{extension} has been loaded and commands synced.")
    except Exception as e:
        await ctx.send(f"Error loading {extension}: {str(e)}")

# Command to unload a cog
@bot.command()
async def unload(ctx, extension):
    """Unload a cog dynamically."""
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await bot.tree.sync()
        await ctx.send(f"{extension} has been unloaded and commands synced.")
    except Exception as e:
        await ctx.send(f"Error unloading {extension}: {str(e)}")
 
# Command: Role Help (Shortened List)
@bot.command(name="rh")
async def role_help(ctx):
    embed = discord.Embed(title="<:currencypaw:1346100210899619901> Role Management Commands", color=discord.Color.blue())

    embed.add_field(name="Create a Role", value="`,rc <role name> <color hex>`", inline=False)
    embed.add_field(name="Delete a Role", value="`,rd <role name>`", inline=False)
    embed.add_field(name="Add Role to User", value="`,ra @user <role name>`", inline=False)
    embed.add_field(name="Remove Role from User", value="`,rr @user <role name>`", inline=False)
    embed.add_field(name="Add Role to Everyone", value="`,raall <role name>`", inline=False)
    embed.add_field(name="Remove Role from Everyone", value="`,rrall <role name>`", inline=False)
    embed.add_field(name="Add Role to Users with a Specific Role", value="`,rin <role1> <role2>`", inline=False)
    embed.add_field(name="Remove Role from Users with a Specific Role", value="`,rout <role1> <role2>`", inline=False)
    embed.add_field(name="List All Roles", value="`,rl`", inline=False)
    embed.add_field(name="Show Role Info", value="`,ri <role name>`", inline=False)
    embed.add_field(name="Change Role Name", value="`,rrename <old> <new>`", inline=False)
    embed.add_field(name="Change Role Color", value="`,rcolor <role> <new color>`", inline=False)
    embed.add_field(name="Change Role Icon", value="`,ri <role name> <emoji or URL>`", inline=False)

    embed.set_footer(text="Use these commands to manage roles efficiently")
    await ctx.send(embed=embed)

import asyncio
import time

@bot.command(name="raall")
@commands.has_permissions(manage_roles=True)
async def role_add_all(ctx, *, role_name: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> Role Not Found",
            description=f"{ctx.author.mention} no role named `{role_name}` exists.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Ensure the role name is spelled correctly.")
        await ctx.send(embed=embed)
        return

    humans = [member for member in guild.members if not member.bot and role not in member.roles]
    total_humans = len(humans)

    if total_humans == 0:
        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> No Eligible Users",
            description=f"{ctx.author.mention} all humans already have the `{role.name}` role.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    # Estimated time calculation based on 1.5 sec per member (Discord rate limits)
    estimated_seconds = total_humans * 1.5
    estimated_hours = estimated_seconds // 3600
    estimated_minutes = (estimated_seconds % 3600) // 60
    estimated_seconds = estimated_seconds % 60

    embed = discord.Embed(
        title=f"<:currencypaw:1346100210899619901> Adding role `{role.name}` to everyone",
        description=(
            f"Total Humans: **{total_humans}**\n"
            f"Estimated Time: **{int(estimated_hours)}h {int(estimated_minutes)}m {int(estimated_seconds)}s**"
        ),
        color=discord.Color.blue()
    )
    status_msg = await ctx.send(embed=embed)

    start_time = time.time()
    success_count = 0

    for member in humans:
        try:
            await member.add_roles(role)
            success_count += 1
            await asyncio.sleep(1.5)  # Discord rate limit
        except discord.Forbidden:
            continue  # Skip members the bot cannot edit

    end_time = time.time()
    time_taken_seconds = int(end_time - start_time)
    time_taken_hours = time_taken_seconds // 3600
    time_taken_minutes = (time_taken_seconds % 3600) // 60
    time_taken_seconds = time_taken_seconds % 60

    embed.title = f"<:currencypaw:1346100210899619901> Role `{role.name}` successfully added to everyone"
    embed.description = (
        f"Added to **{success_count}/{total_humans}** users.\n"
        f"Time Taken: **{time_taken_hours}h {time_taken_minutes}m {time_taken_seconds}s**"
    )
    embed.color = discord.Color.green()
    await status_msg.edit(embed=embed) 

import asyncio
import time

@bot.command(name="rrall")
@commands.has_permissions(manage_roles=True)
async def role_remove_all(ctx, *, role_name: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> Role Not Found",
            description=f"{ctx.author.mention} no role named `{role_name}` exists.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Ensure the role name is spelled correctly.")
        await ctx.send(embed=embed)
        return

    humans_with_role = [member for member in guild.members if not member.bot and role in member.roles]
    total_humans = len(humans_with_role)

    if total_humans == 0:
        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> No Eligible Users",
            description=f"{ctx.author.mention} no human has the `{role.name}` role.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    # Estimated time calculation based on 1.5 sec per member (Discord rate limits)
    estimated_seconds = total_humans * 1.5
    estimated_hours = estimated_seconds // 3600
    estimated_minutes = (estimated_seconds % 3600) // 60
    estimated_seconds = estimated_seconds % 60

    embed = discord.Embed(
        title=f"<:currencypaw:1346100210899619901> Removing role `{role.name}` from everyone",
        description=(
            f"Total Humans: **{total_humans}**\n"
            f"Estimated Time: **{int(estimated_hours)}h {int(estimated_minutes)}m {int(estimated_seconds)}s**"
        ),
        color=discord.Color.blue()
    )
    status_msg = await ctx.send(embed=embed)

    start_time = time.time()
    success_count = 0

    for member in humans_with_role:
        try:
            await member.remove_roles(role)
            success_count += 1
            await asyncio.sleep(1.5)  # Discord rate limit
        except discord.Forbidden:
            continue  # Skip members the bot cannot modify

    end_time = time.time()
    time_taken_seconds = int(end_time - start_time)
    time_taken_hours = time_taken_seconds // 3600
    time_taken_minutes = (time_taken_seconds % 3600) // 60
    time_taken_seconds = time_taken_seconds % 60

    embed.title = f"<:currencypaw:1346100210899619901> `{role.name}` Role successfully removed from everyone"
    embed.description = (
        f"Removed from **{success_count}/{total_humans}** users.\n"
        f"Time Taken: **{time_taken_hours}h {time_taken_minutes}m {time_taken_seconds}s**"
    )
    embed.color = discord.Color.green()
    await status_msg.edit(embed=embed) 

import discord
from discord.ext import commands
from discord.ui import View, Button

class RoleListView(View):
    def __init__(self, roles, per_page=10):
        super().__init__()
        self.roles = roles
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(roles) - 1) // per_page + 1
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page == self.total_pages - 1

    async def update_embed(self, interaction):
        start = self.current_page * self.per_page
        end = start + self.per_page
        role_list = self.roles[start:end]

        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> All the Current Server Roles",
            color=discord.Color.blue()
        )

        role_text = "\n".join([f"**{index}.** {role.mention}" for index, role in enumerate(role_list, start=start + 1)])
        embed.description = role_text
        
        embed.set_footer(text="Use the command ,ri <role name> to view detailed information about any role.")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, disabled=False)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        await self.update_embed(interaction)

@bot.command(name="rl")
async def list_roles(ctx):
    roles = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
    roles = [role for role in roles if role.name != "@everyone"]  # Exclude @everyone, but keep all other roles

    if not roles:
        embed = discord.Embed(
            title="<:currencypaw:1346100210899619901> No Roles Found",
            description="This server has no roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    view = RoleListView(roles)
    first_embed = discord.Embed(
        title="<:currencypaw:1346100210899619901> All the Current Server Roles",
        color=discord.Color.blue()
    )

    role_text = "\n".join([f"**{index}.** {role.mention}" for index, role in enumerate(roles[:10], start=1)])
    first_embed.description = role_text
    first_embed.set_footer(text="Use the command ,ri <role name> to view detailed information about any role.")

    await ctx.send(embed=first_embed, view=view) 

@bot.command(name="ri")
async def role_info(ctx, *, role_name: str = None):
    if role_name is None:
        embed = discord.Embed(title="Error", description="You must specify a role name.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        embed = discord.Embed(title="Error", description="No role exists with that name. Ensure you spelled it correctly and try again.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    # Custom emoji formatting
    right_arrow = "<:rightDoubleArrow:1346853608079097970>"
    success = "<:Success:1346853488738566175>"
    cancel = "<:Cancel:1346853536738316339>"
    profile = "<:Profile:1346853367397220442>"
    managed = "<:managed:1346853575942213662>"

    # Role Permissions Check
    dangerous_perms = ["administrator", "ban_members", "kick_members", "manage_channels", "manage_messages", "manage_roles", "manage_guild"]
    is_dangerous = any(getattr(role.permissions, perm) for perm in dangerous_perms)

    dangerous_emoji = success if is_dangerous else cancel

    # Get permissions list
    perms = [perm.replace("_", " ").title() for perm, value in role.permissions if value]
    perms_text = ", ".join(perms) if perms else "No permissions"

    # Formatting the Embed (No Extra Line Gaps)
    embed = discord.Embed(title=f"What is {role.name}?", color=role.color)
    embed.add_field(name="General Information:", 
                    value=f"{profile} Name: {role.mention}\n"
                          f"{right_arrow} ID: {role.id}\n"
                          f"{right_arrow} Created On: {role.created_at.strftime('%d %B %Y %H:%M')}\n"
                          f"{managed} Managed?: {success if role.managed else cancel}\n"
                          f"{right_arrow} Mentionable?: {success if role.mentionable else cancel}\n"
                          f"{right_arrow} Displayed Separately?: {success if role.hoist else cancel}\n"
                          f"{right_arrow} Position: #{len(ctx.guild.roles) - role.position}\n"
                          f"{right_arrow} Color: {role.color}\n"
                          f"{right_arrow} Dangerous?: {dangerous_emoji}", inline=False)

    # Role Icon if Exists
    if role.icon:
        embed.set_thumbnail(url=role.icon.url)

    embed.set_footer(text=f"Command requested by {ctx.author}")

    # Add permissions at the bottom in small text
    embed.add_field(name="Permissions:", value=f"```{perms_text}```", inline=False)

    await ctx.send(embed=embed)  

# Run the bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
