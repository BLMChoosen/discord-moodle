import os
from dotenv import load_dotenv

load_dotenv()

MOODLE_URL = 'https://seu.moodle.url'  # fixo aqui
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
