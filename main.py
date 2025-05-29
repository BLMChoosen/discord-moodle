import asyncio
import discord
from config import MOODLE_URL, USERNAME, PASSWORD, DISCORD_TOKEN, DISCORD_CHANNEL_ID
from moodle_client import MoodleClient
from discord_bot import DiscordBot
import message_ai

async def main():
    moodle = MoodleClient(MOODLE_URL, USERNAME, PASSWORD)
    moodle.login()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(moodle, DISCORD_CHANNEL_ID, message_ai, intents=intents)
    await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
