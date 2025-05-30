import asyncio
import discord
from config import MOODLE_URL, USERNAME, PASSWORD, DISCORD_TOKEN, DISCORD_CHANNEL_ID
from moodle_client import MoodleClient
from discord_bot import DiscordBot
import message_ai
from datetime import datetime

async def main():
    print('[main] Inicializando MoodleClient...')
    moodle = MoodleClient(MOODLE_URL, USERNAME, PASSWORD)
    moodle.login()

    # Lista todos os cursos e atividades no console
    moodle.print_all_courses_and_assignments()

    print('[main] Inicializando DiscordBot...')
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(moodle, DISCORD_CHANNEL_ID, message_ai, intents=intents)
    print('[main] Iniciando bot do Discord...')
    await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    print('[main] Executando main()...')
    asyncio.run(main())
