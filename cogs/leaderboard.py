import discord
from discord.ext import commands
import asyncio
from database import Database

db = Database()

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_vc_time(self, seconds):
        """Formats VC time as 'X Hours Y Minutes Z Seconds'"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        sec = seconds % 60
        return f"{hours} Hours {minutes} Minutes {sec} Seconds"

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        """Shows the stats of a user"""
        member = member or ctx.author
        messages_sent, vc_seconds = db.get_user_stats(member.id)

        embed = discord.Embed(
            title=f"<:currencypaw:1346100210899619901> Stats for {member.display_name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Messages Sent", value=f"<:currencypaw:1346100210899619901> {messages_sent}", inline=False)
        embed.add_field(name="VC Time", value=f"<:currencypaw:1346100210899619901> {self.format_vc_time(vc_seconds)}", inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="topchat")
    async def top_chat(self, ctx):
        """Shows the top 50 chatters (paginated)"""
        top_chatters = db.get_top_chatters(limit=50)
        pages = []
        
        for i in range(0, len(top_chatters), 10):  # 10 users per page
            embed = discord.Embed(
                title="<:currencypaw:1346100210899619901> Top Chatters",
                color=discord.Color.gold()
            )
            for idx, (user_id, messages) in enumerate(top_chatters[i:i+10], start=i+1):
                user = self.bot.get_user(user_id) or f"User {user_id}"
                embed.add_field(name=f"{idx}. {user}", value=f"[Messages Sent: {messages}]", inline=False)

            pages.append(embed)

        await self.paginate(ctx, pages)

    @commands.command(name="topvc")
    async def top_vc(self, ctx):
        """Shows the top 50 VC users (paginated)"""
        top_vc = db.get_top_vc(limit=50)
        pages = []

        for i in range(0, len(top_vc), 10):  # 10 users per page
            embed = discord.Embed(
                title="<:currencypaw:1346100210899619901> Top VC Users",
                color=discord.Color.gold()
            )
            for idx, (user_id, vc_time) in enumerate(top_vc[i:i+10], start=i+1):
                user = self.bot.get_user(user_id) or f"User {user_id}"
                embed.add_field(name=f"{idx}. {user}", value=f"[VC Time: {self.format_vc_time(vc_time)}]", inline=False)

            pages.append(embed)

        await self.paginate(ctx, pages)

    async def paginate(self, ctx, pages):
        """Handles pagination for topchat and topvc"""
        if not pages:
            await ctx.send("No data available.")
            return

        current_page = 0
        message = await ctx.send(embed=pages[current_page])

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and reaction.emoji in ["◀️", "▶️"]

        while True:
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                if reaction.emoji == "▶️" and current_page < len(pages) - 1:
                    current_page += 1
                    await message.edit(embed=pages[current_page])
                elif reaction.emoji == "◀️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=pages[current_page])

                await message.remove_reaction(reaction.emoji, ctx.author)

            except asyncio.TimeoutError:
                break

def setup(bot):
    bot.add_cog(Leaderboard(bot))
