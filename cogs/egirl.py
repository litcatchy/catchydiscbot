import discord
from discord.ext import commands
import aiohttp
import asyncio
import datetime

# --- CONFIGURE ---
HUGGINGFACE_API_TOKEN = "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"
HUGGINGFACE_MODEL = "tiiuae/falcon-7b-instruct"  # Free model to use, make sure it's available
ALLOWED_CHANNELS = [1359947069472636958, 1339193406269685821]
MEMORY_LIMIT = 5  # how many past messages bot remembers

# --- PERSONALITIES ---
PERSONALITIES = {
    "tsundere": "You are a tsundere girl. You act tough, sassy, dramatic, and use emojis like 🙄😤 but secretly care deep inside. Keep replies short, emotional, dramatic.",
    "sassy": "You are a sassy, confident girl who always has a witty, sarcastic comeback. Use emojis like 😏🙄🤭. Speak casually like a popular girl.",
    "yandere": "You are a yandere girl, sweet and loving, but possessive and a bit obsessive. Speak in a sweet but creepy tone with occasional hints of obsession. Use emojis like 💕😳🖤",
    "teasing": "You are a playful girl who enjoys teasing others, flirty and light-hearted. Use emojis like 😉💋❤️, making fun of the user in a teasing but sweet way.",
    "caring": "You are a caring and loving girlfriend. Always supportive, affectionate, and gentle with your words. Use emojis like 🥰💖🌸. Speak in a comforting and soft tone."
}

class CharacterAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_personality = "tsundere"
        self.chat_memory = {}  # {channel_id: [(user_name, message)]}
        self.last_interaction = {}  # {channel_id: datetime}

    async def query_huggingface(self, prompt):
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
        payload = {"inputs": prompt}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Print the full response for debugging
                        print(f"Response from Huggingface API: {data}")
                        if "generated_text" in data[0]:
                            return data[0]["generated_text"].strip()
                        else:
                            return "Sorry, I couldn't understand that."
                    else:
                        print(f"Failed request: {response.status}")
                        return "Sorry, there was an error processing your request."
        except Exception as e:
            print(f"Error occurred: {e}")
            return "Sorry, an error occurred."

    async def generate_reply(self, channel_id, user_message):
        # Combine memory and new message
        history = self.chat_memory.get(channel_id, [])
        context = "\n".join(f"{user}: {msg}" for user, msg in history[-MEMORY_LIMIT:])
        prompt = f"{PERSONALITIES[self.current_personality]}\nConversation:\n{context}\nUser: {user_message}\nGirl:"

        reply = await self.query_huggingface(prompt)
        if reply.startswith(user_message):
            reply = reply[len(user_message):].strip()
        return reply

    def is_allowed_channel(self, channel_id):
        return channel_id in ALLOWED_CHANNELS

    @commands.command()
    async def setpersonality(self, ctx, *, personality: str):
        """Change the bot's personality (e.g., tsundere, sassy, yandere, etc.)."""
        if personality.lower() in PERSONALITIES:
            self.current_personality = personality.lower()
            await ctx.send(f"Personality set to **{self.current_personality}**!")
        else:
            await ctx.send(f"Available personalities: {', '.join(PERSONALITIES.keys())}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not self.is_allowed_channel(message.channel.id):
            return

        # Reset memory if inactive
        last = self.last_interaction.get(message.channel.id)
        if last and (datetime.datetime.utcnow() - last).seconds > 300:
            self.chat_memory[message.channel.id] = []

        self.last_interaction[message.channel.id] = datetime.datetime.utcnow()

        should_reply = False

        # If bot is pinged
        if self.bot.user in message.mentions:
            should_reply = True

        # If replying to bot's message
        if message.reference:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            if replied_message.author.id == self.bot.user.id:
                should_reply = True

        if should_reply:
            user = message.author.display_name
            content = message.clean_content.replace(f"<@{self.bot.user.id}>", "").strip()

            # Save to memory
            self.chat_memory.setdefault(message.channel.id, []).append((user, content))

            await asyncio.sleep(2)  # Simulate thinking
            reply = await self.generate_reply(message.channel.id, content)
            if not reply:
                reply = "Hmph."

            # Sometimes add a random emoji like 🙄 or 💕
            if "🙄" not in reply and any(word in reply.lower() for word in ["ugh", "whatever", "seriously", "you wish"]):
                reply += " 🙄"
            elif "💕" not in reply and any(word in reply.lower() for word in ["love", "care", "sweet", "please"]):
                reply += " 💖"

            await message.channel.send(reply)

async def setup(bot):
    await bot.add_cog(CharacterAI(bot))
