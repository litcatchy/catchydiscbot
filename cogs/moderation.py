import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def error_embed(self, message):
        embed = discord.Embed(description=f"<:cancel:1346853536738316339> {message}", color=discord.Color.red())
        return embed

    def success_embed(self, message):
        embed = discord.Embed(description=f"<:check:1346853536738316339> {message}", color=discord.Color.green())
        return embed

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if not member:
            return await ctx.send(embed=self.error_embed("Please mention a valid user to kick."))

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=self.error_embed("You cannot kick someone with a higher or equal role."))

        try:
            await member.kick(reason=reason)
            await ctx.send(embed=self.success_embed(f"{member.mention} has been kicked. Reason: {reason}"))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to kick this user."))

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if not member:
            return await ctx.send(embed=self.error_embed("Please mention a valid user to ban."))

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=self.error_embed("You cannot ban someone with a higher or equal role."))

        try:
            await member.ban(reason=reason)
            await ctx.send(embed=self.success_embed(f"{member.mention} has been banned. Reason: {reason}"))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to ban this user."))

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, user: discord.User = None):
        if not user:
            return await ctx.send(embed=self.error_embed("Please provide a valid user ID or mention a user to unban."))

        bans = await ctx.guild.bans()
        banned_users = {entry.user.id: entry.user for entry in bans}

        if user.id not in banned_users:
            return await ctx.send(embed=self.error_embed("This user is not banned."))

        try:
            await ctx.guild.unban(user)
            await ctx.send(embed=self.success_embed(f"{user.mention} has been unbanned."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to unban this user."))

    @commands.has_permissions(moderate_members=True)
    @commands.command()
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason="No reason provided"):
        if not member:
            return await ctx.send(embed=self.error_embed("Please mention a valid user to timeout."))

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=self.error_embed("You cannot timeout someone with a higher or equal role."))

        if not duration:
            return await ctx.send(embed=self.error_embed("Please provide a valid duration (e.g., 10m, 1h, 1d)."))

        time_units = {"m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_units or not duration[:-1].isdigit():
            return await ctx.send(embed=self.error_embed("Invalid duration format. Use (e.g., 10m, 1h, 1d)."))

        timeout_seconds = int(duration[:-1]) * time_units[unit]
        timeout_until = discord.utils.utcnow() + datetime.timedelta(seconds=timeout_seconds)

        try:
            await member.timeout(timeout_until, reason=reason)
            await ctx.send(embed=self.success_embed(f"{member.mention} has been timed out for {duration}. Reason: {reason}"))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to timeout this user."))

    @commands.has_permissions(moderate_members=True)
    @commands.command()
    async def untimeout(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send(embed=self.error_embed("Please mention a valid user to remove timeout."))

        if member == ctx.guild.owner:
            return await ctx.send(embed=self.error_embed("Skill issue, slaves cannot use the command on the server owner."))

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=self.error_embed("You cannot remove timeout from someone with a higher or equal role."))

        if not member.timed_out_until:
            return await ctx.send(embed=self.error_embed("This user is not timed out."))

        try:
            await member.timeout(None)
            await ctx.send(embed=self.success_embed(f"{member.mention} has been removed from timeout."))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("I don't have permission to remove timeout from this user."))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
