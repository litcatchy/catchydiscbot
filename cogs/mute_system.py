import discord
from discord.ext import commands

class MuteSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def imute(self, ctx, member: discord.Member = None, *, reason: str = None):
        """ Mutes a member by removing their ability to send images and embed links. """

        # Check if the command user has permission
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You need the **Moderate Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Ensure a member is mentioned
        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to mute.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Prevent muting the server owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if a reason is provided
        if not reason:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> Providing a reason is necessary because this action will be logged.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member has a higher role
        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot mute someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member is already muted
        overwrite = ctx.channel.overwrites_for(member)
        if overwrite.attach_files is False and overwrite.embed_links is False:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> {member.mention} already does not have image and embed link permissions.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        # Remove attach files and embed links permissions
        overwrite.attach_files = False
        overwrite.embed_links = False
        await ctx.channel.set_permissions(member, overwrite=overwrite)

        # Success message
        embed = discord.Embed(
            description=f"<:success:1346853488738566175> {member.mention} has been muted from sending images and embed links.\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def iunmute(self, ctx, member: discord.Member = None):
        """ Restores a member's ability to send images and embed links. """

        # Check if the command user has permission
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You need the **Moderate Members** permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Ensure a member is mentioned
        if not member:
            embed = discord.Embed(
                description="<:mention:1347449690849022092> You must mention a user to unmute.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Prevent unmuting the server owner
        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="Skill issue, slaves cannot use the command on the server owner.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member has a higher role
        if ctx.author.top_role <= member.top_role:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> You cannot unmute someone with a higher or equal role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check if the member already has permissions
        overwrite = ctx.channel.overwrites_for(member)
        if overwrite.attach_files is None and overwrite.embed_links is None:
            embed = discord.Embed(
                description=f"<:cancel:1346853536738316339> {member.mention} already has image and embed link permissions.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        # Restore attach files and embed links permissions
        overwrite.attach_files = None
        overwrite.embed_links = None
        await ctx.channel.set_permissions(member, overwrite=overwrite)

        # Success message
        embed = discord.Embed(
            description=f"<:success:1346853488738566175> {member.mention} can now send images and embed links again.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MuteSystem(bot))
