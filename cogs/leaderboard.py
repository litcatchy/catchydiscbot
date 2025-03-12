import discord
from discord.ext import commands
import asyncio
from database import Database  # Importing database

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    def format_vc_time(self, seconds):
        """Formats VC time into hours, minutes, and seconds."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    @commands.command(name="stats")
    async def user_stats(self, ctx, member: discord.Member = None):
        """Shows user stats (messages sent & VC time)."""
        member = member or ctx.author  # Default to command sender

        messages, vc_time = self.db.get_user_stats(member.id)
        vc_formatted = self.format_vc_time(vc_time)

        embed = discord.Embed(
            title=f"<:currencypaw:1346100210899619901> {member.display_name}'s Stats",
            color=discord.Color.blue()
        )
        embed.add_field(name="<:currencypaw:1346100210899619901> Messages Sent", value=f"`{messages}`", inline=True)
        embed.add_field(name="<:currencypaw:1346100210899619901> VC Time", value=f"`{vc_formatted}`", inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="topchat")
    async def top_chat(self, ctx):
        """Shows top message senders with pagination."""
        data = self.db.get_top_chatters()  # Gets top 50 users
        await self.paginate_leaderboard(ctx, data, "<:currencypaw:1346100210899619901> Top Message Senders", "Messages")

    @commands.command(name="topvc")
    async def top_vc(self, ctx):
        """Shows top VC users with pagination."""
        data = self.db.get_top_vc()  # Gets top 50 users
        await self.paginate_leaderboard(ctx, data, "<:currencypaw:1346100210899619901> Top VC Users", "VC Time", vc_time=True)

    async def paginate_leaderboard(self, ctx, data, title, label, vc_time=False):
        """Handles leaderboard pagination for both topchat & topvc."""
        pages = []
        per_page = 10  # 10 users per page

        if not data:
            embed = discord.Embed(
                title=title,
                description="No data available yet.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
            return await ctx.send(embed=embed)

        for i in range(0, len(data), per_page):
            chunk = data[i:i + per_page]  # Get 10 users per page
            description = ""

            for index, (user_id, value) in enumerate(chunk, start=i+1):
                user = self.bot.get_user(user_id) or f"User {user_id}"
                value_text = self.format_vc_time(value) if vc_time else f"{value} messages"
                description += f"`{index}.` **{user}** → {value_text}\n"

            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {i//per_page + 1} / {max(1, len(data)//per_page + (1 if len(data) % per_page else 0))}")
            pages.append(embed)

        await self.paginate(ctx, pages)

    async def paginate(self, ctx, pages):
        """Handles pagination with reaction buttons."""
        if len(pages) == 1:
            return await ctx.send(embed=pages[0])

        current_page = 0
        message = await ctx.send(embed=pages[current_page])
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                await message.remove_reaction(reaction.emoji, user)

                if str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                    current_page += 1
                elif str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1

                await message.edit(embed=pages[current_page])
            except asyncio.TimeoutError:
                break

        await message.clear_reactions()

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
