import discord
from discord.ext import commands
import re

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Function to get color from name or hex
    def get_color(self, color_input):
        if not color_input:
            return discord.Color.default()
        try:
            if color_input.startswith("#"):  # Hex code
                return discord.Color(int(color_input[1:], 16))
            else:  # Named color
                return getattr(discord.Color, color_input.lower())()
        except (AttributeError, ValueError):
            return discord.Color.default()

    # Function to extract role name and color from input
    def extract_role_and_color(self, text):
        words = text.split()
        color = words[-1].lower() if words[-1].lower() in dir(discord.Color) or re.match(r"^#[0-9A-Fa-f]{6}$", words[-1]) else None
        role_name = " ".join(words[:-1]) if color else " ".join(words)
        return role_name, color

    # Command: Create Role
    @commands.command(name="rc")
    @commands.has_permissions(manage_roles=True)
    async def role_create(self, ctx, *, input_text: str):
        role_name, color = self.extract_role_and_color(input_text)
        guild = ctx.guild
        role_color = self.get_color(color)

        new_role = await guild.create_role(name=role_name, color=role_color, permissions=discord.Permissions(manage_roles=True))

        embed = discord.Embed(color=role_color)
        embed.description = f"<:success:1346853488738566175> Role `{new_role.name}` created successfully!"
        embed.add_field(name="Color", value=color if color else "Default", inline=False)
        embed.set_footer(text=f"Created by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # Command: Delete Role
    @commands.command(name="rd")
    @commands.has_permissions(manage_roles=True)
    async def role_delete(self, ctx, *, role_name: str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            embed = discord.Embed(color=discord.Color.red())
            embed.description = f"<:cancel:1346853536738316339> No role named `{role_name}` exists."
            embed.set_footer(text="Ensure the role name is spelled correctly.")
            await ctx.send(embed=embed)
            return

        await role.delete()

        embed = discord.Embed(color=discord.Color.red())
        embed.description = f"<:success:1346853488738566175> Role `{role.name}` deleted successfully!"
        embed.set_footer(text=f"Deleted by {ctx.author.display_name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
