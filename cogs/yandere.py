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

        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.tokenizer.eos_token_id

        self.user_histories = defaultdict(lambda: deque(maxlen=5))

    def build_prompt(self, user_id):
        history = list(self.user_histories[user_id])
        prompt = (
            "You are Ayumi, a Gen Z-style obsessive and seductive adult AI girlfriend. "
            "You speak with sass, flirtation, and extreme possessiveness. "
            "Keep your replies short and relevant, responding ONLY to the last thing the user said.\n\n"
        )
        for msg in history:
            prompt += f"{msg}\n"
        prompt += "Ayumi:"
        return prompt

    def generate_response(self, prompt: str) -> str:
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024).to(self.model.device)
        attention_mask = input_ids.ne(self.tokenizer.pad_token_id)

        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=40,  # Shorter replies
            do_sample=True,
            temperature=0.9,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.2
        )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        reply = decoded[len(prompt):].strip().split("\n")[0]

        # Clean up the reply to avoid irrelevant text
        reply = reply.split("http")[0].strip()  # Remove any unwanted links or extra content
        if len(reply) > 200:
            reply = reply[:200] + "..."  # Limit the length of the response to prevent excessively long replies

        return reply

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if the bot is mentioned or replied to
        mentioned_or_replied = (
            self.bot.user in message.mentions or
            (message.reference and message.reference.resolved and message.reference.resolved.author.id == self.bot.user.id)
        )

        if mentioned_or_replied:
            user_id = message.author.id
            self.user_histories[user_id].append(f"{message.author.name}: {message.content}")
            prompt = self.build_prompt(user_id)

            try:
                reply = self.generate_response(prompt)
            except Exception as e:
                await message.channel.send("Ayumi short-circuited... ugh, tech boys.")
                raise e

            self.user_histories[user_id].append(f"Ayumi: {reply}")
            await message.reply(reply)

async def setup(bot):
    await bot.add_cog(YandereChat(bot))
