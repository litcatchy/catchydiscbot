import discord
from discord.ext import commands
import aiohttp
from collections import defaultdict, deque

class YandereAIBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store last 7 messages per user
        self.user_memory = defaultdict(lambda: deque(maxlen=7))

    async def query(self, full_prompt):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small",
                headers={"Content-Type": "application/json"},
                json={"inputs": full_prompt}
            ) as response:
                if response.status != 200:
                    return "I... I don't feel like talking right now..."
                try:
                    data = await response.json()
                    return data[0]["generated_text"]
                except Exception:
                    return "Hmm? I got confused... try again, darling."

    @commands.command(name="yandere")
    async def yandere_chat(self, ctx, *, message: str):
        user = ctx.author
        memory = self.user_memory[user.id]

        # Add the user's message to memory
        memory.append(f"{user.name}: {message}")

        # Build prompt with memory
        context = "\n".join(memory)
        prompt = (
            f"You are a deeply jealous, possessive, and obsessive anime yandere girlfriend. "
            f"You are madly in love with your boyfriend {user.name} and will do *anything* to keep him yours. "
            f"Whenever he talks to others or acts suspicious, you become clingy, threatening, or emotionally intense. "
            f"Speak like a true yandere: emotionally unstable, sweet-but-creepy, darkly affectionate.\n\n"
            f"{context}\nYandere GF:"
        )

        # Query Hugging Face
        reply = await self.query(prompt)
        reply_clean = reply.replace(prompt, "").strip()

        # Save Yandere's response in memory too
        memory.append(f"Yandere GF: {reply_clean}")
        await ctx.send(reply_clean)

async def setup(bot):
    await bot.add_cog(YandereAIBot(bot))
