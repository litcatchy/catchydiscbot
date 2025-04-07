import discord
from discord.ext import commands
from collections import deque
from datetime import datetime

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages = {}  # Stores deleted messages per guild
        self.sniped_reactions = {}  # Stores removed reactions per guild

    async def paginate(self, ctx, data_list, title):
        """Handles pagination using buttons."""
        if not data_list:
            return await ctx.send(embed=discord.Embed(description="<:currencypaw:1346100210899619901> No data available.", color=discord.Color.red()))

        index = 0
        total = len(data_list)

        async def update_embed():
            entry = data_list[index]
            embed = discord.Embed(title=title, description=entry, color=discord.Color.blue())
            embed.set_footer(text=f"Page {index + 1}/{total}")
            return embed

        class PaginationView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.timeout = 30

            @discord.ui.button(label="Page Back", style=discord.ButtonStyle.primary, disabled=True)
            async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal index
                index -= 1
                if index == 0:
                    button.disabled = True
                self.children[1].disabled = False
                await interaction.response.edit_message(embed=await update_embed(), view=self)

            @discord.ui.button(label="Page Next", style=discord.ButtonStyle.primary)
            async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal index
                index += 1
                if index == total - 1:
                    button.disabled = True
                self.children[0].disabled = False
                await interaction.response.edit_message(embed=await update_embed(), view=self)

        view = PaginationView()
        if total == 1:
            view.children[0].disabled = True
            view.children[1].disabled = True

        await ctx.send(embed=await update_embed(), view=view)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Stores deleted messages."""
        if message.guild:
            self.sniped_messages.setdefault(message.guild.id, deque(maxlen=3)).appendleft((message.author, message.content))

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """Stores removed reactions with message content."""
        if reaction.message.guild:
            self.sniped_reactions.setdefault(reaction.message.guild.id, deque(maxlen=3)).appendleft(
                (user, str(reaction.emoji), reaction.message.content, reaction.message.jump_url)
            )

    @commands.command(name="s")
    async def snipe_message(self, ctx):
        """Snipe last 3 deleted messages."""
        data_list = [
            f"**Message by {author.mention}**\n{content}"
            for author, content in self.sniped_messages.get(ctx.guild.id, [])
        ]
        await self.paginate(ctx, data_list, "<:currencypaw:1346100210899619901> Deleted Messages")

    @commands.command(name="rs")
    async def snipe_reaction(self, ctx):
        """Snipe last 3 removed reactions, including message content."""
        data_list = [
            f"**Reaction by {user.mention}**\nReacted with {emoji} on:\n**Message:** {content}\n[Jump to message]({message_url})"
            for user, emoji, content, message_url in self.sniped_reactions.get(ctx.guild.id, [])
        ]
        await self.paginate(ctx, data_list, "<:currencypaw:1346100210899619901> Removed Reactions")

    @commands.command(name="cs")
    async def clear_snipe(self, ctx):
        """Clear deleted message snipes."""
        if not ctx.author.guild_permissions.manage_messages:
            embed = discord.Embed(description="You will need manage messages permission to execute that command.", color=discord.Color.red())
            return await ctx.send(embed=embed)

        snipes = self.sniped_messages.get(ctx.guild.id, [])
        if not snipes:
            embed = discord.Embed(description="There are no recent deleted messages to clear snipes.", color=discord.Color.red())
            return await ctx.send(embed=embed)

        # Prepare cleared messages for logs
        cleared_messages = "\n".join(
            f"- {author}: {content}" for author, content in snipes
        ) or "No messages."

        # Log channel
        log_channel = self.bot.get_channel(1339898523407355945)
        if log_channel:
            embed = discord.Embed(
                title="Snipe Cleared",
                description=f"Deleted message snipes have been cleared by {ctx.author.mention} (`{ctx.author.id}`)",
                color=discord.Color.green()
            )
            embed.add_field(name="Guild", value=f"{ctx.guild.name} (`{ctx.guild.id}`)", inline=False)
            embed.add_field(name="Channel", value=f"{ctx.channel.name} (`{ctx.channel.id}`)", inline=False)
            embed.add_field(name="Cleared Messages", value=cleared_messages, inline=False)
            embed.set_footer(text=f"Clear sniper log | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            await log_channel.send(embed=embed)

        # Clear snipes and react
        self.sniped_messages[ctx.guild.id].clear()
        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(Snipe(bot))
