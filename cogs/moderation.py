import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, message, success=True):
        """Helper function to send embed messages with emojis."""
        emoji = "<:success:1346853488738566175>" if success else "<:cancel:1346853536738316339>"
        embed = discord.Embed(description=f"{emoji} {message}", color=0x00FF00 if success else 0xFF0000)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            await self.send_embed(ctx, "Skill issue, slaves cannot use the command on the server owner.", success=False)
            return
        await member.kick(reason=reason)
        await self.send_embed(ctx, f"{member.mention} has been kicked. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            await self.send_embed(ctx, "Skill issue, slaves cannot use the command on the server owner.", success=False)
            return
        await member.ban(reason=reason)
        await self.send_embed(ctx, f"{member.mention} has been banned. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        bans = await ctx.guild.bans()
        if not any(ban_entry.user.id == user_id for ban_entry in bans):
            await self.send_embed(ctx, "This user is not banned.", success=False)
            return
        await ctx.guild.unban(user)
        await self.send_embed(ctx, f"{user.mention} has been unbanned.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        if member == ctx.guild.owner:
            await self.send_embed(ctx, "Skill issue, slaves cannot use the command on the server owner.", success=False)
            return
        
        unit_multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if not (duration[-1] in unit_multipliers and duration[:-1].isdigit()):
            await self.send_embed(ctx, "Invalid time format! Use s/m/h/d (e.g., 10m).", success=False)
            return
        
        seconds = int(duration[:-1]) * unit_multipliers[duration[-1]]
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)

        await member.timeout(until, reason=reason)
        await self.send_embed(ctx, f"{member.mention} has been timed out for {duration}. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        if member.timed_out_until is None:
            await self.send_embed(ctx, "This user is not timed out.", success=False)
            return
        await member.timeout(None)
        await self.send_embed(ctx, f"{member.mention} has been untimed out.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
