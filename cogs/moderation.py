import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, success: bool, message: str):
        embed = discord.Embed(
            description=f"{'<:check:1346853536738316338>' if success else '<:cancel:1346853536738316339>'} {message}",
            color=0x57F287 if success else 0xED4245
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members)
    async def kick(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if not member:
            return await self.send_embed(ctx, False, "You must mention a user to kick.")
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, False, "Skill issue, slaves cannot use the command on the server owner.")
        try:
            await member.kick(reason=reason)
            await self.send_embed(ctx, True, f"Successfully kicked {member.mention}.")
        except discord.Forbidden:
            await self.send_embed(ctx, False, "I don't have permission to kick this user.")

    @commands.command()
    @commands.has_permissions(ban_members)
    async def ban(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if not member:
            return await self.send_embed(ctx, False, "You must mention a user to ban.")
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, False, "Skill issue, slaves cannot use the command on the server owner.")
        try:
            await member.ban(reason=reason)
            await self.send_embed(ctx, True, f"Successfully banned {member.mention}.")
        except discord.Forbidden:
            await self.send_embed(ctx, False, "I don't have permission to ban this user.")

    @commands.command()
    @commands.has_permissions(ban_members)
    async def unban(self, ctx, user_id: int = None):
        if not user_id:
            return await self.send_embed(ctx, False, "You must provide a valid user ID to unban.")
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await self.send_embed(ctx, True, f"Successfully unbanned {user.mention}.")
        except discord.NotFound:
            await self.send_embed(ctx, False, "That user ID is not banned or does not exist.")
        except discord.Forbidden:
            await self.send_embed(ctx, False, "I don't have permission to unban this user.")

    @commands.command()
    @commands.has_permissions(moderate_members)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None, *, reason="No reason provided"):
        if not member:
            return await self.send_embed(ctx, False, "You must mention a user to timeout.")
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, False, "Skill issue, slaves cannot use the command on the server owner.")
        if not duration:
            return await self.send_embed(ctx, False, "You must specify a duration (e.g., `10m`, `1h`, `1d`).")

        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            unit = duration[-1]
            if unit not in time_units:
                raise ValueError("Invalid duration unit.")
            time_amount = int(duration[:-1])
            total_seconds = time_amount * time_units[unit]
            until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=total_seconds)
            await member.timeout(until, reason=reason)
            await self.send_embed(ctx, True, f"Successfully timed out {member.mention} for {duration}.")
        except ValueError:
            await self.send_embed(ctx, False, "Invalid duration format. Use `s`, `m`, `h`, or `d` (e.g., `10m`, `1h`, `1d`).")
        except discord.Forbidden:
            await self.send_embed(ctx, False, "I don't have permission to timeout this user.")

    @commands.command()
    @commands.has_permissions(moderate_members)
    async def untimeout(self, ctx, member: discord.Member = None):
        if not member:
            return await self.send_embed(ctx, False, "You must mention a user to remove timeout.")
        if member == ctx.guild.owner:
            return await self.send_embed(ctx, False, "Skill issue, slaves cannot use the command on the server owner.")
        try:
            await member.timeout(None)
            await self.send_embed(ctx, True, f"Successfully removed timeout from {member.mention}.")
        except discord.Forbidden:
            await self.send_embed(ctx, False, "I don't have permission to remove timeout from this user.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
