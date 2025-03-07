from discord.ext import commands
import discord

class RoleAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command: Add Role to User
    @commands.command(name="ra")
    @commands.has_permissions(manage_roles=True)
    async def role_add(self, ctx, member: discord.Member, *, role_name: str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> No role named `{role_name}` exists.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Ensure the role name is spelled correctly.")
            await ctx.send(embed=embed)
            return  

        if not ctx.guild.me.guild_permissions.manage_roles:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I do not have permission to **Manage Roles**.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return  

        if role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I cannot assign `{role.name}` because it is higher or equal to my highest role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return  

        await member.add_roles(role)

        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Added Role", value=role.name, inline=False)
        embed.set_footer(text=f"Executed by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # Command: Remove Role from User
    @commands.command(name="rr")
    @commands.has_permissions(manage_roles=True)
    async def role_remove(self, ctx, member: discord.Member, *, role_name: str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)

        if role is None:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> No role named `{role_name}` exists.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Ensure the role name is spelled correctly.")
            await ctx.send(embed=embed)
            return

        if role not in member.roles:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> {member.mention} does not have the `{role.name}` role.",
                color=discord.Color.orange()
            )
            embed.set_footer(text="Ensure the role name is spelled correctly.")
            await ctx.send(embed=embed)
            return

        await member.remove_roles(role)

        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Removed Role", value=role.name, inline=False)
        embed.set_footer(text=f"Executed by {ctx.author.display_name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleAssignment(bot))
