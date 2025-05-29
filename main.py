import asyncio
import os
from dotenv import load_dotenv
from moodle_client import MoodleClient
from discord_bot import DiscordBot
import discord

load_dotenv()  # carrega as variáveis do .env

MOODLE_URL = 'https://seu.moodle.url'  # fixo aqui mesmo
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
COURSE_ID = int(os.getenv('COURSE_ID'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

async def main():
    moodle = MoodleClient(MOODLE_URL, USERNAME, PASSWORD, COURSE_ID)
    moodle.login()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(moodle, DISCORD_CHANNEL_ID, intents=intents)
    await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
