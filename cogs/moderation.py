import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed(self, ctx, title, description, color):
        embed = discord.Embed(title=title, description=description, color=color)
        await ctx.send(embed=embed)

    # Handle missing arguments globally
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                         f"Missing argument: `{error.param.name}`.", discord.Color.red())
        elif isinstance(error, commands.BadArgument):
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                         "Invalid argument provided.", discord.Color.red())
        elif isinstance(error, commands.MemberNotFound):
            return await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                         "User not found.", discord.Color.red())

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided."):
        """Kick a member from the server."""
        try:
            await member.kick(reason=reason)
            await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                  f"{member.mention} has been kicked.\n**Reason:** {reason}", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I don't have permission to kick this member.", discord.Color.red())

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided."):
        """Ban a member from the server."""
        try:
            await member.ban(reason=reason)
            await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                  f"{member.mention} has been banned.\n**Reason:** {reason}", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I don't have permission to ban this member.", discord.Color.red())

    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, time: int, *, reason="No reason provided."):
        """Timeout a member (in minutes)."""
        try:
            duration = discord.utils.utcnow() + discord.timedelta(minutes=time)
            await member.timeout(duration, reason=reason)
            await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                  f"{member.mention} has been timed out for `{time}` minutes.\n**Reason:** {reason}", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I don't have permission to timeout this member.", discord.Color.red())

    @commands.command(name="untimeout")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Remove timeout from a member."""
        try:
            await member.timeout(None)
            await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                  f"{member.mention} has been untimed out.", discord.Color.green())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I don't have permission to untimeout this member.", discord.Color.red())

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User):
        """Unban a previously banned user."""
        try:
            bans = await ctx.guild.bans()
            for ban_entry in bans:
                if ban_entry.user.id == user.id:
                    await ctx.guild.unban(user)
                    return await self.send_embed(ctx, "<:success:1346853488738566175> Success",
                                                 f"{user.mention} has been unbanned.", discord.Color.green())

            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  f"{user.mention} is not banned.", discord.Color.red())
        except discord.Forbidden:
            await self.send_embed(ctx, "<:cancel:1346853536738316339> Error",
                                  "I don't have permission to unban this user.", discord.Color.red())

async def setup(bot):
    await bot.add_cog(Moderation(bot))
