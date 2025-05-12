
import discord
from discord.ext import commands

class StaffBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Update these user IDs manually for weekly bests
        self.best_coowner_id = 1353508240784363621 
        self.best_admin_id = 1187556818570973194  
        self.best_staff_id = 1363093037130977362

        # Role IDs
        self.coowner_role_id = 1370413469865611274
        self.admin_role_id = 1370413505840287935
        self.staff_role_id = 1370413526656745492

    @commands.command(aliases=["sb"])
    async def staffboard(self, ctx):
        guild = ctx.guild

        # Fetch members with each role
        coowners = [m for m in guild.members if self.coowner_role_id in [r.id for r in m.roles]]
        admins = [m for m in guild.members if self.admin_role_id in [r.id for r in m.roles]]
        staff = [m for m in guild.members if self.staff_role_id in [r.id for r in m.roles]]

        def format_list(members, best_id, emoji, role_title):
            lines = []
            best_member = next((m for m in members if m.id == best_id), None)
            if best_member:
                lines.append(f"1. {best_member.mention} [Best {role_title} of the Week {emoji}]")
                members = [m for m in members if m.id != best_id]
            for i, member in enumerate(members, start=len(lines)+1):
                lines.append(f"{i}. {member.mention}")
            return "\n".join(lines) if lines else "None"

        embed = discord.Embed(title="Best Staff of the Week", color=discord.Color.purple())

        embed.add_field(
            name="**Co-Owners**",
            value=format_list(coowners, self.best_coowner_id, "<:coowner:1371463627705421844>", "co-owner"),
            inline=False,
        )
        embed.add_field(
            name="**Admins**",
            value=format_list(admins, self.best_admin_id, "<:admin:1371463646370201630>", "admin"),
            inline=False,
        )
        embed.add_field(
            name="**Staff**",
            value=format_list(staff, self.best_staff_id, "<:staff:1371463638375993374>", "staff"),
            inline=False,
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StaffBoard(bot))
