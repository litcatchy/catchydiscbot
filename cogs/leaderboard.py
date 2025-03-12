import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import sqlite3

# Owner ID to restrict certain commands
OWNER_ID = 230022649844203522  # Replace with your actual owner ID

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('stats.db')
    conn.row_factory = sqlite3.Row
    return conn

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to view stats for a specific user
    @commands.command()
    async def stats(self, ctx, member: discord.Member = None):
        """View a user's chat messages and VC time."""
        if member is None:
            member = ctx.author  # Default to the command user's stats

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaderboard WHERE user_id = ?", (str(member.id),))
        user_data = cursor.fetchone()

        if user_data:
            messages_sent = user_data['messages_sent']
            vc_time_seconds = user_data['vc_time']
            hours = vc_time_seconds // 3600
            minutes = (vc_time_seconds % 3600) // 60
            seconds = vc_time_seconds % 60
            vc_time_formatted = f"{hours}h {minutes}m {seconds}s"
            
            embed = discord.Embed(title=f"{member.name}'s Stats", color=discord.Color.green())
            embed.add_field(name="Messages Sent", value=f"{messages_sent} <:currencypaw:1346100210899619901>", inline=False)
            embed.add_field(name="VC Time", value=f"{vc_time_formatted} <:currencypaw:1346100210899619901>", inline=False)
        else:
            embed = discord.Embed(title="No Data", description="No data found for this user.", color=discord.Color.red())

        conn.close()
        await ctx.send(embed=embed)

    # Command to view the top 10 chatters
    @commands.command()
    async def topchat(self, ctx, page: int = 1):
        """Shows the top 10 chatters with pagination."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate the OFFSET based on the current page
        limit = 10
        offset = (page - 1) * limit

        cursor.execute("SELECT * FROM leaderboard ORDER BY messages_sent DESC LIMIT ? OFFSET ?", (limit, offset))
        top_chatters = cursor.fetchall()

        if top_chatters:
            embed = discord.Embed(title="Top Chatters", color=discord.Color.green())
            for i, user in enumerate(top_chatters, start=(page - 1) * limit + 1):
                messages_sent = user['messages_sent']
                embed.add_field(name=f"{i}. {user['user_id']}", value=f"Messages: {messages_sent} <:currencypaw:1346100210899619901>", inline=False)
        else:
            embed = discord.Embed(title="No Data", description="No top chatters found.", color=discord.Color.red())

        conn.close()

        # Create pagination buttons
        buttons = View()
        if page > 1:
            buttons.add_item(Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="previous"))
        buttons.add_item(Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next"))

        # Send embed and buttons
        message = await ctx.send(embed=embed, view=buttons)

        # Handle button interactions
        def check(interaction):
            return interaction.message.id == message.id and interaction.user == ctx.author

        try:
            interaction = await self.bot.wait_for("interaction", timeout=60.0, check=check)

            if interaction.data["custom_id"] == "next":
                await message.edit(embed=await self.paginate_topchat(page + 1), view=buttons)
            elif interaction.data["custom_id"] == "previous" and page > 1:
                await message.edit(embed=await self.paginate_topchat(page - 1), view=buttons)

            await interaction.response.defer()

        except Exception:
            pass

    async def paginate_topchat(self, page):
        conn = get_db_connection()
        cursor = conn.cursor()

        limit = 10
        offset = (page - 1) * limit

        cursor.execute("SELECT * FROM leaderboard ORDER BY messages_sent DESC LIMIT ? OFFSET ?", (limit, offset))
        top_chatters = cursor.fetchall()

        embed = discord.Embed(title="Top Chatters", color=discord.Color.green())
        for i, user in enumerate(top_chatters, start=(page - 1) * limit + 1):
            messages_sent = user['messages_sent']
            embed.add_field(name=f"{i}. {user['user_id']}", value=f"Messages: {messages_sent} <:currencypaw:1346100210899619901>", inline=False)

        conn.close()
        return embed

    # Command to view the top 10 VC users
    @commands.command()
    async def topvc(self, ctx, page: int = 1):
        """Shows the top 10 VC users with pagination."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate the OFFSET based on the current page
        limit = 10
        offset = (page - 1) * limit

        cursor.execute("SELECT * FROM leaderboard ORDER BY vc_time DESC LIMIT ? OFFSET ?", (limit, offset))
        top_vc = cursor.fetchall()

        if top_vc:
            embed = discord.Embed(title="Top VC Users", color=discord.Color.green())
            for i, user in enumerate(top_vc, start=(page - 1) * limit + 1):
                vc_time_seconds = user['vc_time']
                hours = vc_time_seconds // 3600
                minutes = (vc_time_seconds % 3600) // 60
                seconds = vc_time_seconds % 60
                vc_time_formatted = f"{hours}h {minutes}m {seconds}s"

                embed.add_field(name=f"{i}. {user['user_id']}", value=f"VC Time: {vc_time_formatted} <:currencypaw:1346100210899619901>", inline=False)
        else:
            embed = discord.Embed(title="No Data", description="No top VC users found.", color=discord.Color.red())

        conn.close()

        # Create pagination buttons
        buttons = View()
        if page > 1:
            buttons.add_item(Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="previous"))
        buttons.add_item(Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next"))

        # Send embed and buttons
        message = await ctx.send(embed=embed, view=buttons)

        # Handle button interactions
        def check(interaction):
            return interaction.message.id == message.id and interaction.user == ctx.author

        try:
            interaction = await self.bot.wait_for("interaction", timeout=60.0, check=check)

            if interaction.data["custom_id"] == "next":
                await message.edit(embed=await self.paginate_topvc(page + 1), view=buttons)
            elif interaction.data["custom_id"] == "previous" and page > 1:
                await message.edit(embed=await self.paginate_topvc(page - 1), view=buttons)

            await interaction.response.defer()

        except Exception:
            pass

    async def paginate_topvc(self, page):
        conn = get_db_connection()
        cursor = conn.cursor()

        limit = 10
        offset = (page - 1) * limit

        cursor.execute("SELECT * FROM leaderboard ORDER BY vc_time DESC LIMIT ? OFFSET ?", (limit, offset))
        top_vc = cursor.fetchall()

        embed = discord.Embed(title="Top VC Users", color=discord.Color.green())
        for i, user in enumerate(top_vc, start=(page - 1) * limit + 1):
            vc_time_seconds = user['vc_time']
            hours = vc_time_seconds // 3600
            minutes = (vc_time_seconds % 3600) // 60
            seconds = vc_time_seconds % 60
            vc_time_formatted = f"{hours}h {minutes}m {seconds}s"

            embed.add_field(name=f"{i}. {user['user_id']}", value=f"VC Time: {vc_time_formatted} <:currencypaw:1346100210899619901>", inline=False)

        conn.close()
        return embed

    # Command to update a user's stats (chat messages and VC time)
    @commands.command()
    @commands.is_owner()
    async def updatestats(self, ctx, member: discord.Member, messages_sent: int, vc_time: int):
        """Manually update a user's stats."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO leaderboard (user_id, messages_sent, vc_time) VALUES (?, ?, ?)", 
                       (str(member.id), messages_sent, vc_time))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="Stats Updated", description=f"Updated stats for {member.name}.", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Command to update the leaderboard stats every 5 minutes
    @commands.command()
    @commands.is_owner()
    async def updatelead5m(self, ctx):
        """Updates the leaderboard every 5 minutes."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaderboard")
        all_data = cursor.fetchall()

        for data in all_data:
            user_id = data['user_id']
            messages_sent = data['messages_sent']
            vc_time = data['vc_time']
            cursor.execute("UPDATE leaderboard SET messages_sent = ?, vc_time = ? WHERE user_id = ?", 
                           (messages_sent, vc_time, user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="Leaderboard Updated", description="Leaderboard stats updated successfully.", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Command to update top VC stats
    @commands.command()
    @commands.is_owner()
    async def updatetopvc(self, ctx):
        """Update top VC stats."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaderboard ORDER BY vc_time DESC")
        top_vc = cursor.fetchall()

        for i, data in enumerate(top_vc):
            user_id = data['user_id']
            vc_time = data['vc_time']
            cursor.execute("UPDATE leaderboard SET vc_time = ? WHERE user_id = ?", 
                           (vc_time, user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="Top VC Updated", description="Top VC stats updated successfully.", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Command to update top chat stats
    @commands.command()
    @commands.is_owner()
    async def updatetopchat(self, ctx):
        """Update top chat stats."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaderboard ORDER BY messages_sent DESC")
        top_chatters = cursor.fetchall()

        for i, data in enumerate(top_chatters):
            user_id = data['user_id']
            messages_sent = data['messages_sent']
            cursor.execute("UPDATE leaderboard SET messages_sent = ? WHERE user_id = ?", 
                           (messages_sent, user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="Top Chat Updated", description="Top chat stats updated successfully.", color=discord.Color.green())
        await ctx.send(embed=embed)

    # Updates both top chat and top VC at once
    @commands.command()
    @commands.is_owner()
    async def updatetopall(self, ctx):
        """Update both top VC and top chat stats."""
        await self.updatetopvc(ctx)
        await self.updatetopchat(ctx)
        embed = discord.Embed(title="Top Stats Updated", description="Both top VC and top chat stats updated successfully.", color=discord.Color.green())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Leaderboard(bot))
    
