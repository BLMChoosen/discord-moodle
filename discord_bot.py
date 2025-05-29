import discord
from discord.ext import tasks

class DiscordBot(discord.Client):
    def __init__(self, moodle_client, channel_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moodle_client = moodle_client
        self.channel_id = channel_id
        self.check_deadlines.start()

    async def on_ready(self):
        print(f'[DiscordBot] Logado como {self.user}.')

    @tasks.loop(minutes=60)
    async def check_deadlines(self):
        try:
            assignments = self.moodle_client.get_assignments()
            channel = self.get_channel(self.channel_id)
            if not channel:
                print(f'[DiscordBot] Canal {self.channel_id} não encontrado.')
                return

            for a in assignments:
                # Aqui tu pode fazer a lógica de avisar se o prazo tá perto, etc.
                await channel.send(f"Atividade: **{a['name']}** - Prazo: {a['due']}")

        except Exception as e:
            print(f'[DiscordBot] Erro ao checar prazos: {e}')
