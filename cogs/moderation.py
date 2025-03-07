import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def error_embed(self, message):
        return discord.Embed(description=f"<:cancel:1346853536738316339> {message}", color=discord.Color.red())

    def success_embed(self, message):
        return discord.Embed(description=f"<:check:1346853536738316339> {message}", color=discord.Color.green())

    async def get_member(self, ctx, arg):
        try:
            return await commands.MemberConverter().convert(ctx, arg)
        except commands.MemberNotFound:
            await ctx.send(embed=self.error_embed("Invalid user (not in the server)."))
            return None

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, *, member_arg: str = None):
        member = await self.get_member(ctx, member_arg)
        if not member:
            return

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        try:
            await member.kick(reason="No reason provided")
            await ctx.send(embed=self.success_embed(f"{member.mention} has been kicked."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to kick this user."))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, *, member_arg: str = None):
        member = await self.get_member(ctx, member_arg)
        if not member:
            return

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        try:
            await member.ban(reason="No reason provided")
            await ctx.send(embed=self.success_embed(f"{member.mention} has been banned."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to ban this user."))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User = None):
        if not user:
            return await ctx.send(embed=self.error_embed("Please provide a valid user ID or mention a user to unban."))

        banned_users = [entry async for entry in ctx.guild.bans()]
        if not any(entry.user.id == user.id for entry in banned_users):
            return await ctx.send(embed=self.error_embed("This user is not banned."))

        try:
            await ctx.guild.unban(user)
            await ctx.send(embed=self.success_embed(f"{user.mention} has been unbanned."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to unban this user."))

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member_arg: str = None, duration: str = None):
        member = await self.get_member(ctx, member_arg)
        if not member:
            return

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        if not duration:
            return await ctx.send(embed=self.error_embed("Please provide a valid duration (e.g., 10m, 1h, 1d)."))

        time_units = {"m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_units or not duration[:-1].isdigit():
            return await ctx.send(embed=self.error_embed("Invalid duration format. Use (e.g., 10m, 1h, 1d)."))

        timeout_seconds = int(duration[:-1]) * time_units[unit]
        timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=timeout_seconds)

        try:
            await member.timeout(timeout_until, reason="No reason provided")
            await ctx.send(embed=self.success_embed(f"{member.mention} has been timed out for {duration}."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to timeout this user."))

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member_arg: str = None):
        member = await self.get_member(ctx, member_arg)
        if not member:
            return

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        if not member.timed_out_until:
            return await ctx.send(embed=self.error_embed("This user is not timed out."))

        try:
            await member.timeout(None)
            await ctx.send(embed=self.success_embed(f"{member.mention} has been removed from timeout."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to remove timeout from this user."))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
