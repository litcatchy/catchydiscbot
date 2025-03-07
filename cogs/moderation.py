import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_permissions(ctx, perm):
        """Custom check to send an embed instead of raising an exception."""
        if not getattr(ctx.author.guild_permissions, perm, False):
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You need the **{perm.replace('_', ' ').title()}** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return False
        return True

    def permission_check(perm):
        """Decorator to apply the check_permissions function."""
        async def predicate(ctx):
            return await Moderation.check_permissions(ctx, perm)
        return commands.check(predicate)

    @commands.command()
    @permission_check("moderate_members")
    async def timeout(self, ctx, member: discord.Member = None, duration: int = None, *, reason: str = "No reason provided"):
        """Timeout a member."""
        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot timeout the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot timeout someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration), reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been timed out for **{duration} minutes**.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    @permission_check("moderate_members")
    async def untimeout(self, ctx, member: discord.Member = None):
        """Remove timeout from a member."""
        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to remove timeout.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} is no longer timed out.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Untimed out by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to remove timeout.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    @permission_check("kick_members")
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kicks a user from the server."""

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to kick.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot kick the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} has been kicked.\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> Failed to kick.\nError: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command()
    @permission_check("ban_members")
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Bans a user from the server."""

        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to ban.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.guild.owner:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot ban the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> You cannot ban {member.mention} because they have a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            await ctx.guild.ban(member, reason=reason)
            embed = discord.Embed(
                description=f"<:success:1346853488738566175> {member.mention} got banned by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> I do not have permission to ban {member.mention}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                description=f"{ctx.author.mention} <:cancel:1346853536738316339> The user {member.mention} does not exist or is already banned.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
