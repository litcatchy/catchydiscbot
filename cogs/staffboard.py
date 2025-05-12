import discord
from discord.ext import commands

class StaffBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Best of the week (manually update these mentions)
        self.best_coowner = "<@1353508240784363621>"  
        self.best_admin = "<@1187556818570973194>"
        self.best_staff = "<@1363093037130977362>"

        # Emoji usage (use animated emoji format with 'a' prefix if animated)
        self.emoji_coowner = "<a:coowner:1371463627705421844>"  
        self.emoji_admin = "<a:admin:1371463646370201630>"  
        self.emoji_staff = "<a:staff:1371463638375993374>"  

        # Role IDs
        self.coowner_role_id = 1370413469865611274
        self.admin_role_id = 1370413505840287935
        self.staff_role_id = 1370413526656745492

    @commands.command(aliases=["sb"])
    async def staffboard(self, ctx):
        guild = ctx.guild

        coowners = [member.mention for member in guild.members if self.coowner_role_id in [role.id for role in member.roles]]
        admins = [member.mention for member in guild.members if self.admin_role_id in [role.id for role in member.roles]]
        staffs = [member.mention for member in guild.members if self.staff_role_id in [role.id for role in member.roles]]

        coowner_list = [f"1. {self.best_coowner} {self.emoji_coowner}"] + [
            f"{i+2}. {m}" for i, m in enumerate(member for member in coowners if member != self.best_coowner)
        ]
        admin_list = [f"1. {self.best_admin} {self.emoji_admin}"] + [
            f"{i+2}. {m}" for i, m in enumerate(member for member in admins if member != self.best_admin)
        ]
        staff_list = [f"1. {self.best_staff} {self.emoji_staff}"] + [
            f"{i+2}. {m}" for i, m in enumerate(member for member in staffs if member != self.best_staff)
        ]

        embed = discord.Embed(title="Staffboard [Best of the week]", color=discord.Color.purple())
        embed.add_field(name="**Co-Owners**", value="\n".join(coowner_list) or "None", inline=False)
        embed.add_field(name="**Admins**", value="\n".join(admin_list) or "None", inline=False)
        embed.add_field(name="**Staffs**", value="\n".join(staff_list) or "None", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StaffBoard(bot))
