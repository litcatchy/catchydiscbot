import discord
from discord.ext import commands
import asyncio

class RoleDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rdall")
    async def rdall(self, ctx):
        if ctx.author != ctx.guild.owner:
            embed = discord.Embed(
                description="<:cancel:1346853536738316339> Nuke menu commands can only be executed by the server owner",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        roles_to_delete = []
        reserves = []

        for role in ctx.guild.roles:
            if role.is_bot_managed() or role.managed:
                continue  # Skip bot-managed roles
            if role >= ctx.guild.me.top_role or role == ctx.guild.default_role:
                continue  # Skip roles above bot or @everyone
            if role in ctx.guild.owner.roles:
                continue  # Skip owner’s own roles (extra safety)

            roles_to_delete.append(role)

        count = len(roles_to_delete)
        estimated = count  # 1s per deletion

        start_embed = discord.Embed(
            title="Role Deletion In Progress",
            description=f"Deleting `{count}` roles...\nEstimated time: `{estimated} seconds`",
            color=discord.Color.orange()
        )
        message = await ctx.send(embed=start_embed)

        for role in roles_to_delete:
            perm_text = []
            perms = role.permissions
            if perms.administrator:
                perm_text.append("Administrator")
            if perms.kick_members:
                perm_text.append("Kick Members")
            if perms.ban_members:
                perm_text.append("Ban Members")
            if perms.manage_roles:
                perm_text.append("Manage Roles")
            if perms.manage_guild:
                perm_text.append("Manage Server")
            if perms.moderate_members:
                perm_text.append("Timeout Members")

            perm_summary = ", ".join(perm_text) if perm_text else "[null]"

            try:
                await role.delete(reason="Deleted via ,rdall command")
                reserves.append(f"**Role deleted**: `{role.name}` *({perm_summary})*")
            except discord.Forbidden:
                reserves.append(f"**Skipped (No Perms)**: `{role.name}` *({perm_summary})*")
            except discord.HTTPException:
                reserves.append(f"**Failed**: `{role.name}` *({perm_summary})*")
            await asyncio.sleep(1)  # Discord rate limit

        final_embed = discord.Embed(
            description=f"<:success:1346853488738566175> `{len(roles_to_delete)}` roles have been deleted.",
            color=discord.Color.green()
        )

        final_embed.add_field(name="Reserves:", value="\n".join(reserves[:25]) or "[None]", inline=False)
        if len(reserves) > 25:
            final_embed.set_footer(text=f"And {len(reserves) - 25} more...")

        await message.edit(embed=final_embed)

async def setup(bot):
    await bot.add_cog(RoleDelete(bot))
