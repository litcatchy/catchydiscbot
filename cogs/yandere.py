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
            f"You are a highly possessive, obsessive, and emotional yandere girlfriend. "
            f"Your love for {user.name} is absolute, and you’ll do anything to keep them by your side. "
            f"You are incredibly protective, jealous, and clingy when it comes to your partner. "
            f"Whenever {user.name} talks to someone else or shows any attention to anyone, you become jealous and may act possessively. "
            f"Your tone is sweet but sometimes dark, emotional, and intense. You speak in a way that feels like you care deeply but also have a dangerous side. "
            f"You love {user.name} more than anything else and constantly fear losing them. Keep the tone emotional, affectionate, and sometimes obsessive.\n\n"
            f"Context of the conversation:\n{context}\nYandere GF:"
        )

        # Query Hugging Face
        reply = await self.query(prompt)
        reply_clean = reply.replace(prompt, "").strip()

        # Save Yandere's response in memory too
        memory.append(f"Yandere GF: {reply_clean}")
        await ctx.send(reply_clean)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Prevent the bot from replying to its own messages
        if message.author == self.bot.user:
            return

        # Check if the bot was mentioned in the message (pinged)
        if self.bot.user.mentioned_in(message):
            # Fetch last user message in memory and reply to it
            user = message.author
            memory = self.user_memory[user.id]

            # Get the last message (most recent) in memory
            if memory:
                last_user_message = memory[-1]
                # Generate response based on last user message
                reply = await self.query(f"Yandere GF: {last_user_message}\nYandere GF:")

                # Send the bot's reply
                await message.channel.send(reply)
            else:
                await message.channel.send("You haven’t said anything to me yet, darling... Why are you ignoring me?")

        # Check if the message is a reply to one of the bot's own messages
        if message.reference and message.reference.message_id:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            if referenced_message.author == self.bot.user:
                # Get the last message and generate a response
                reply = await self.query(f"Yandere GF: {referenced_message.content}\nYandere GF:")
                await message.channel.send(reply)

async def setup(bot):
    await bot.add_cog(YandereAIBot(bot))
