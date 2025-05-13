import discord
from discord.ext import commands
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import defaultdict, deque

class YandereChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_name = "distilgpt2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

        # Set pad token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.tokenizer.eos_token_id

        # Store user chat history, only the last 5 messages
        self.user_histories = defaultdict(lambda: deque(maxlen=5))

    def build_prompt(self, user_id):
        history = list(self.user_histories[user_id])[-5:]  # Get last 5 lines max
        prompt = "You are a obsessive, possessive, jealous seductive AI named Ayumi. You speak like you're deeply obsessed with the user, mixing love with possessiveness."
        for msg in history:
            prompt += f"\n{msg}"
        prompt += "\nAyumi:"
        return prompt

    def generate_response(self, prompt: str) -> str:
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024).to(self.model.device)
        attention_mask = input_ids.ne(self.tokenizer.pad_token_id)

        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.9,
            top_p=0.95
        )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        reply = decoded[len(prompt):].strip()
        return reply

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if the bot is pinged or replied to
        if self.bot.user in message.mentions or (message.reference and message.reference.resolved and message.reference.resolved.author.id == self.bot.user.id):
            user_id = message.author.id

            self.user_histories[user_id].append(f"{message.author.name}: {message.content}")
            prompt = self.build_prompt(user_id)

            try:
                reply = self.generate_response(prompt)
            except Exception as e:
                await message.channel.send("I encountered an error processing that...")
                raise e

            self.user_histories[user_id].append(f"Ayumi: {reply}")
            await message.reply(reply)
        else:
            # Log message for history without replying
            self.user_histories[message.author.id].append(f"{message.author.name}: {message.content}")

async def setup(bot):
    await bot.add_cog(YandereChat(bot))
