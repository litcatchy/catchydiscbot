import discord
from discord.ext import commands

# Set up bot intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # Required to manage roles
intents.message_content = True  # Required for message-based commands

# Initialize bot with prefix ","
bot = commands.Bot(command_prefix=",", intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Command: Create Role
@bot.command(name="role_create", aliases=["rc"])
@commands.has_permissions(manage_roles=True)
async def role_create(ctx, role_name: str, *, color: str = None):
    guild = ctx.guild

    # Convert color input to a valid discord.Color
    if color:
        try:
            if color.startswith("#"):  # Hex code format
                role_color = discord.Color(int(color[1:], 16))
            else:  # Named colors
                role_color = getattr(discord.Color, color.lower())()
        except AttributeError:
            role_color = discord.Color.default()
    else:
        role_color = discord.Color.default()

    # Create the role
    new_role = await guild.create_role(name=role_name, color=role_color, permissions=discord.Permissions(manage_roles=True))

    # Embed response
    embed = discord.Embed(title="✅ Role Created Successfully", color=role_color)
    embed.add_field(name="Role Name", value=new_role.name, inline=False)
    embed.add_field(name="Color", value=color if color else "Default", inline=False)
    embed.set_footer(text=f"Created by {ctx.author.display_name}")

    await ctx.send(embed=embed)
bot.run("YOUR_BOT_TOKEN")
