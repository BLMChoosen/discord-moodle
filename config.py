import os
from dotenv import load_dotenv

load_dotenv(override=True)

MOODLE_URL = 'https://moodle.farroupilha.ifrs.edu.br'  # fixo aqui
USERNAME = os.environ.get('USERNAME')  # deve ser 'davi.oliz' conforme .env
print(f'[config] USERNAME carregado: {USERNAME}')
PASSWORD = os.environ.get('PASSWORD')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))
