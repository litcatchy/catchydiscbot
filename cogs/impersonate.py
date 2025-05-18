import discord
from discord.ext import commands

class Impersonate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="impersonate")
    async def impersonate(self, ctx, member: discord.Member, *, message: str):
        try:
            await ctx.message.delete()  # Delete the invoking message

            # Create a webhook
            webhook = await ctx.channel.create_webhook(name=member.display_name)
            avatar_bytes = await member.display_avatar.read()

            # Send the impersonated message
            await webhook.send(
                content=message,
                username=member.display_name,
                avatar_url=member.display_avatar.url
            )

            # Delete the webhook
            await webhook.delete()

        except Exception as e:
            await ctx.send(f"Error: {e}", delete_after=5)

async def setup(bot):
    await bot.add_cog(Impersonate(bot))
