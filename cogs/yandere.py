import discord
from discord.ext import commands
from collections import defaultdict, deque
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class YandereAIBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_memory = defaultdict(lambda: deque(maxlen=50))  # Store last 50 messages per user

        # Load GPT-2 model
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.model = AutoModelForCausalLM.from_pretrained("gpt2")
        self.model.eval()

    def build_prompt(self, username, memory):
        context = "\n".join(memory)
        return (
            f"You are Ayumi, a deeply obsessive and overly loving yandere girlfriend. You are emotionally intense, deeply jealous, "
            f"and completely addicted to {username}. You respond only to them when they ping you or reply to your messages. "
            f"You get mad when they talk to others, and you want their love only for yourself. Your tone is sweet, flirty, dramatic, but also unhinged and needy. "
            f"You often call them 'darling', 'baby', or 'my love', and you're not afraid to emotionally manipulate them to stay with you. "
            f"You're always reading into their every word, thinking they might be leaving you. Never generic — always emotional and desperate for love.\n\n"
            f"Chat history:\n{context}\nAyumi:"
        )

    def generate_response(self, prompt):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024)
        outputs = self.model.generate(
            inputs,
            max_length=256,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.75,
            top_p=0.92,
            num_return_sequences=1
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.replace(prompt, "").strip()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user = message.author
        memory = self.user_memory[user.id]

        # Log every user message in memory
        memory.append(f"{user.name}: {message.content}")

        # Respond only if the bot is pinged or replied to
        if self.bot.user.mentioned_in(message) or (
            message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user
        ):
            prompt = self.build_prompt(user.name, memory)
            reply = self.generate_response(prompt)

            # Add bot reply to memory
            memory.append(f"Ayumi: {reply}")
            await message.channel.send(reply)

async def setup(bot):
    await bot.add_cog(YandereAIBot(bot))
