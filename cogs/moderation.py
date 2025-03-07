import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, title, description, color):
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kicks a member from the server."""
        try:
            await member.kick(reason=reason)
            await self.send_embed(ctx, f"<:success:1346853488738566175> Kicked {member.name}",
                                  f"Reason: {reason}", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I do not have permission to kick this member.", discord.Color.red())

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Bans a member from the server."""
        try:
            await member.ban(reason=reason)
            await self.send_embed(ctx, f"<:success:1346853488738566175> Banned {member.name}",
                                  f"Reason: {reason}", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I do not have permission to ban this member.", discord.Color.red())

    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, time: int, *, reason="No reason provided"):
        """Times out a member for a certain duration in minutes."""
        try:
            duration = discord.utils.utcnow() + discord.utils.timedelta(minutes=time)
            await member.timeout(duration, reason=reason)
            await self.send_embed(ctx, f"<:success:1346853488738566175> Timed out {member.name}",
                                  f"Duration: {time} minutes\nReason: {reason}", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I do not have permission to timeout this member.", discord.Color.red())

    @commands.command(name="untimeout")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Removes timeout from a member."""
        try:
            await member.timeout(None)
            await self.send_embed(ctx, f"<:success:1346853488738566175> Removed timeout from {member.name}",
                                  "", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I do not have permission to remove timeout.", discord.Color.red())

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User):
        """Unbans a user from the server."""
        try:
            bans = await ctx.guild.bans()
            for entry in bans:
                if entry.user.id == user.id:
                    await ctx.guild.unban(user)
                    await self.send_embed(ctx, f"<:success:1346853488738566175> Unbanned {user.name}",
                                          "", discord.Color.green())
                    return
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "This user is not banned.", discord.Color.red())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I do not have permission to unban this user.", discord.Color.red())

async def setup(bot):
    await bot.add_cog(Moderation(bot))
