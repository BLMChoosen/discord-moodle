import discord
from discord.ext import tasks
import asyncio

class DiscordBot(discord.Client):
    def __init__(self, moodle_client, channel_id, message_ai, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moodle_client = moodle_client
        self.channel_id = channel_id
        self.message_ai = message_ai
        self.checked_assignments = set()  # Pra não floodar toda hora
        self.check_assignments.start()

    async def on_ready(self):
        print(f'[DiscordBot] Logado como {self.user}.')

    @tasks.loop(minutes=60)
    async def check_assignments(self):
        try:
            courses = self.moodle_client.get_courses()
            channel = self.get_channel(self.channel_id)
            if not channel:
                print(f'[DiscordBot] Canal {self.channel_id} não encontrado.')
                return

            for course in courses:
                assignments = self.moodle_client.get_assignments(course['id'])
                for a in assignments:
                    key = (course['id'], a['name'], a['due'])
                    if key not in self.checked_assignments:
                        msg = self.message_ai.generate_message(course['name'], a)
                        await channel.send(msg)
                        self.checked_assignments.add(key)

        except Exception as e:
            print(f'[DiscordBot] Erro ao checar prazos: {e}')
