import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_error(self, ctx, message):
        embed = discord.Embed(description=f"<:cancel:1346853536738316339> {message}", color=discord.Color.red())
        await ctx.send(embed=embed)

    async def send_success(self, ctx, message):
        embed = discord.Embed(description=f"<:success:1346853536738316339> {message}", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.has_permissions(kick_members)
    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if not member:
            return await self.send_error(ctx, "Invalid user. Please mention a valid member.")

        if member == ctx.guild.owner:
            return await self.send_error(ctx, "Skill issue, slaves cannot use the command on the server owner.")

        await member.kick(reason=reason)
        await self.send_success(ctx, f"{member.mention} has been kicked. Reason: {reason}")

    @commands.has_permissions(ban_members)
    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if not member:
            return await self.send_error(ctx, "Invalid user. Please mention a valid member.")

        if member == ctx.guild.owner:
            return await self.send_error(ctx, "Skill issue, slaves cannot use the command on the server owner.")

        await member.ban(reason=reason)
        await self.send_success(ctx, f"{member.mention} has been banned. Reason: {reason}")

    @commands.has_permissions(ban_members)
    @commands.command(name="unban")
    async def unban(self, ctx, user: discord.User = None):
        if not user:
            return await self.send_error(ctx, "Invalid user. Please provide a valid user ID or mention.")

        bans = [ban_entry.user async for ban_entry in ctx.guild.bans()]
        if user not in bans:
            return await self.send_error(ctx, f"{user.mention} is not banned.")

        await ctx.guild.unban(user)
        await self.send_success(ctx, f"{user.mention} has been unbanned.")

    @commands.has_permissions(moderate_members)
    @commands.command(name="timeout")
    async def timeout(self, ctx, member: discord.Member = None, duration: int = 0, *, reason="No reason provided"):
        if not member:
            return await self.send_error(ctx, "Invalid user. Please mention a valid member.")

        if member == ctx.guild.owner:
            return await self.send_error(ctx, "Skill issue, slaves cannot use the command on the server owner.")

        duration_seconds = duration * 60  # Convert minutes to seconds
        await member.timeout(discord.utils.utcnow().replace(microsecond=0) + discord.timedelta(seconds=duration_seconds), reason=reason)
        await self.send_success(ctx, f"{member.mention} has been timed out for {duration} minutes. Reason: {reason}")

    @commands.has_permissions(moderate_members)
    @commands.command(name="untimeout")
    async def untimeout(self, ctx, member: discord.Member = None):
        if not member:
            return await self.send_error(ctx, "Invalid user. Please mention a valid member.")

        if member == ctx.guild.owner:
            return await self.send_error(ctx, "Skill issue, slaves cannot use the command on the server owner.")

        await member.timeout(None)
        await self.send_success(ctx, f"{member.mention} has been untimed out.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
