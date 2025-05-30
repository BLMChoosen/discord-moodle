import discord
from discord.ext import tasks
import asyncio
from datetime import datetime, timedelta
import utils

class DiscordBot(discord.Client):
    def __init__(self, moodle_client, channel_id, message_ai, *args, **kwargs):
        # Não cria intents aqui, usa as que chegam via kwargs
        super().__init__(*args, **kwargs)

        self.moodle_client = moodle_client
        self.channel_id = channel_id
        self.message_ai = message_ai
        self.checked_assignments = set()
        self.logged_in = False  # Adicionado para controlar estado de login
        self.first_run_done = False

    async def on_ready(self):
        print(f'[DiscordBot] Logado como {self.user}.')

        self.logged_in = True  # Assume que já está logado se chegou aqui

        print('\n=== Canais de texto disponíveis ===')
        for guild in self.guilds:
            print(f'Servidor: {guild.name} (ID: {guild.id})')
            for channel in guild.text_channels:
                print(f'  Canal: {channel.name} (ID: {channel.id})')

        test_channel = self.get_channel(self.channel_id)
        if test_channel:
            try:
                await test_channel.send('✅ Bot está ativo e tem acesso a este canal!')
                print(f'[DiscordBot] Mensagem de teste enviada no canal {self.channel_id}.')
            except Exception as e:
                print(f'[DiscordBot] Erro ao mandar mensagem de teste: {e}')
        else:
            print(f'[DiscordBot] Canal {self.channel_id} não encontrado no cache.')

        # Primeira execução: só avisa das atividades pendentes (prazo >= hoje)
        await self.notify_pending_assignments_first_run()
        self.first_run_done = True

        # Inicie o loop só agora, após login e ready
        self.check_assignments.start()

    async def notify_pending_assignments_first_run(self):
        channel = self.get_channel(self.channel_id)
        if not channel:
            print(f'[DiscordBot] Canal {self.channel_id} não encontrado para envio inicial.')
            return

        print('[DiscordBot] Enviando atividades pendentes (primeira execução)...')
        courses = self.moodle_client.get_courses()
        now = datetime.now()
        for course in courses:
            assignments = self.moodle_client.get_assignments(course['id'])
            msg_lines = []
            for a in assignments:
                due_dt = utils.parse_moodle_date(a['due'])
                # Só mostra se o prazo ainda não passou (>= agora)
                if due_dt and due_dt >= now:
                    msg_lines.append(f'**{a["name"]}**\nVencimento: `{a["due"]}`')
                    self.checked_assignments.add((course['id'], a['name'], a['due']))
            if msg_lines:
                msg = f'**Curso:** {course["name"]}\n' + '\n\n'.join(msg_lines)
                await channel.send(msg)
                await asyncio.sleep(2)
        print('[DiscordBot] Atividades pendentes enviadas!')

    @tasks.loop(minutes=20)
    async def check_assignments(self):
        if not self.logged_in or not self.first_run_done:
            print('[DiscordBot] Não logado no Moodle ou primeira execução não concluída, pulando verificação...')
            return

        try:
            courses = self.moodle_client.get_courses()
            channel = self.get_channel(self.channel_id)
            if not channel:
                print(f'[DiscordBot] Canal {self.channel_id} não encontrado.')
                return

            print('\n=== Verificando novas atividades e lembretes ===')
            now = datetime.now()
            today = now.date()
            for course in courses:
                assignments = self.moodle_client.get_assignments(course['id'])
                for a in assignments:
                    due_dt = utils.parse_moodle_date(a['due'])
                    # Só ignora se o prazo já passou
                    if not due_dt or due_dt < now:
                        continue
                    key = (course['id'], a['name'], a['due'])
                    # Nova atividade (após primeira execução)
                    if key not in self.checked_assignments:
                        msg = (
                            f'@everyone\n'
                            f'🚨 **Nova tarefa lançada!**\n'
                            f'Curso: **{course["name"]}**\n'
                            f'Atividade: **{a["name"]}**\n'
                            f'Prazo: `{a["due"]}`'
                        )
                        await channel.send(msg)
                        self.checked_assignments.add(key)
                    # Lembretes de 7, 3, 1 dia
                    else:
                        dias = (due_dt.date() - today).days
                        if dias in [7, 3, 1]:
                            msg = (
                                f'@everyone\n'
                                f'⏰ **Faltam {dias} dia{"s" if dias > 1 else ""} para o prazo!**\n'
                                f'Curso: **{course["name"]}**\n'
                                f'Atividade: **{a["name"]}**\n'
                                f'Prazo: `{a["due"]}`'
                            )
                            await channel.send(msg)
            print('Verificação de tarefas concluída.')
        except Exception as e:
            print(f'[DiscordBot] Erro ao checar prazos: {e}')
