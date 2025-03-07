import discord
from discord.ext import commands

class RoleAddRemove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        embed = discord.Embed(
            description=f"<:success:1346853488738566175> `{role.name}` added to {member.mention} by {ctx.author.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

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
            await ctx.send(embed=embed)
            return  

        if role not in member.roles:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:mention:1347449690849022092> {member.mention} does not have the `{role.name}` role.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return  

        await member.remove_roles(role)

        embed = discord.Embed(
            description=f"<:success:1346853488738566175> `{role.name}` removed from {member.mention} by {ctx.author.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @role_add.error
    @role_remove.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Missing arguments. Please provide a user and role name.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> Invalid user or role provided.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> An unknown error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleAddRemove(bot))
