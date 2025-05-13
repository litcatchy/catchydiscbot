import discord
from discord.ext import commands
import aiohttp
from collections import defaultdict, deque

class YandereAIBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store user messages separately using defaultdict of deque (up to 7 messages per user)
        self.user_memory = defaultdict(lambda: deque(maxlen=7))

    async def query(self, full_prompt):
        # Use Hugging Face API to generate responses
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

        # Add the user's message to memory (only store up to 7 messages)
        memory.append(f"{user.name}: {message}")

        # Build prompt with memory context
        context = "\n".join(memory)
        prompt = (
            f"You are a highly possessive, obsessive, and emotional yandere girlfriend. "
            f"Your love for {user.name} is absolute, and you’ll do anything to keep them by your side. "
            f"You're incredibly protective, jealous, and clingy when it comes to your partner. "
            f"Whenever {user.name} talks to someone else or shows any attention to anyone, you become jealous and may act possessively. "
            f"Your tone is sweet but sometimes dark, emotional, and intense. You love {user.name} more than anything else and constantly fear losing them. "
            f"Keep the tone emotional, affectionate, and sometimes obsessive.\n\n"
            f"Context of the conversation:\n{context}\nYandere GF:"
        )

        # Query Hugging Face for response
        reply = await self.query(prompt)
        reply_clean = reply.replace(prompt, "").strip()

        # Save Yandere GF's response in memory too
        memory.append(f"Yandere GF: {reply_clean}")
        await ctx.send(reply_clean)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Prevent bot from responding to its own messages
        if message.author == self.bot.user:
            return

        # Check if the bot was mentioned in the message (pinged)
        if self.bot.user.mentioned_in(message):
            user = message.author
            memory = self.user_memory[user.id]

            # If there are messages in memory, generate a response based on the last user message
            if memory:
                last_user_message = memory[-1]
                context = "\n".join(memory)
                prompt = (
                    f"You are a highly possessive, obsessive, and emotional yandere girlfriend. "
                    f"Your love for {user.name} is absolute, and you’ll do anything to keep them by your side. "
                    f"You're incredibly protective, jealous, and clingy when it comes to your partner. "
                    f"Whenever {user.name} talks to someone else or shows any attention to anyone, you become jealous and may act possessively. "
                    f"Your tone is sweet but sometimes dark, emotional, and intense. You love {user.name} more than anything else and constantly fear losing them. "
                    f"Keep the tone emotional, affectionate, and sometimes obsessive.\n\n"
                    f"Context of the conversation:\n{context}\nYandere GF:"
                )

                # Query Hugging Face for response based on the memory context
                reply = await self.query(prompt)
                reply_clean = reply.replace(prompt, "").strip()

                # Save Yandere GF's response in memory too
                memory.append(f"Yandere GF: {reply_clean}")
                await message.channel.send(reply_clean)
            else:
                # If there's no memory, say the user hasn't spoken yet
                await message.channel.send("You haven’t said anything to me yet, darling... Why are you ignoring me?")
        
        # Check if the message is a reply to one of the bot's own messages
        if message.reference and message.reference.message_id:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            if referenced_message.author == self.bot.user:
                # Generate a response based on the bot's previous message
                reply = await self.query(f"Yandere GF: {referenced_message.content}\nYandere GF:")
                await message.channel.send(reply)

async def setup(bot):
    await bot.add_cog(YandereAIBot(bot))
