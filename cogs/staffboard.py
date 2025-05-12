import discord
from discord.ext import commands

class StaffBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Best of the week user IDs – update these in code
        self.best_coowner_id = 1353508240784363621  
        self.best_admin_id = 1187556818570973194    
        self.best_staff_id = 1363093037130977362   

        # Emojis
        self.coowner_emoji = "<:coowner:1371463627705421844>"
        self.admin_emoji = "<:admin:1371463646370201630>"
        self.staff_emoji = "<:staff:1371463638375993374>"

        # Role IDs
        self.coowner_role_id = 1370413469865611274
        self.admin_role_id = 1370413505840287935
        self.staff_role_id = 1370413526656745492

    @commands.command(aliases=["sb"])
    async def staffboard(self, ctx):
        guild = ctx.guild

        # Get members by roles
        coowners = [m for m in guild.members if self.coowner_role_id in [r.id for r in m.roles]]
        admins = [m for m in guild.members if self.admin_role_id in [r.id for r in m.roles]]
        staff = [m for m in guild.members if self.staff_role_id in [r.id for r in m.roles]]

        def format_list(members, best_id, emoji, title):
            formatted = []
            if any(m.id == best_id for m in members):
                best = next(m for m in members if m.id == best_id)
                formatted.append(f"1. {best.mention} [Best {title} of the Week {emoji}]")
                members.remove(best)
            for i, member in enumerate(members, start=len(formatted)+1):
                formatted.append(f"{i}. {member.mention}")
            return "\n".join(formatted) if formatted else "None"

        coowner_text = format_list(coowners, self.best_coowner_id, self.coowner_emoji, "co-owner")
        admin_text = format_list(admins, self.best_admin_id, self.admin_emoji, "admin")
        staff_text = format_list(staff, self.best_staff_id, self.staff_emoji, "staff")

        embed = discord.Embed(color=discord.Color.purple())
        embed.add_field(name="**Co-Owners**", value=coowner_text, inline=False)
        embed.add_field(name="**Admins**", value=admin_text, inline=False)
        embed.add_field(name="**Staff**", value=staff_text, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StaffBoard(bot))
