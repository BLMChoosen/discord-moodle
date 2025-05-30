import discord
from discord.ext import tasks
import asyncio
from datetime import datetime, timedelta
import utils
from utils import now_brasilia

class DiscordBot(discord.Client):
    def __init__(self, moodle_client, channel_id, message_ai, *args, **kwargs):
        # Não cria intents aqui, usa as que chegam via kwargs
        super().__init__(*args, **kwargs)

        self.moodle_client = moodle_client
        self.channel_id = channel_id
        self.message_ai = message_ai
        self.checked_assignments = set()
        self.sent_reminders = set()  # (course_id, assignment_name, due, dias_para_prazo)
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
        now = now_brasilia()
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

    @tasks.loop(minutes=5)
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

            now = now_brasilia()
            print(f'\n[DiscordBot] Verificando novas atividades e lembretes em {now.strftime("%d/%m/%Y %H:%M:%S")} (horário de Brasília)')
            today = now.date()
            for course in courses:
                assignments = self.moodle_client.get_assignments(course['id'])
                for a in assignments:
                    due_dt = utils.parse_moodle_date(a['due'])
                    if not due_dt or due_dt < now:
                        continue
                    key = (course['id'], a['name'], a['due'])
                    delta = due_dt - now
                    dias = delta.days
                    horas, resto = divmod(delta.seconds, 3600)
                    minutos = resto // 60
                    print(f'[DiscordBot] {course["name"]} - {a["name"]}: falta {dias}d {horas}h {minutos}m para o prazo ({a["due"]})')
                    tempo_falta_str = f"Faltam {dias}d {horas}h {minutos}m para o prazo."
                    # Nova atividade (após primeira execução)
                    if key not in self.checked_assignments:
                        msg = (
                            f'@everyone\n'
                            f'🚨 **Nova tarefa lançada!**\n'
                            f'Curso: **{course["name"]}**\n'
                            f'Atividade: **{a["name"]}**\n'
                            f'Prazo: `{a["due"]}`\n'
                            f'{tempo_falta_str}'
                        )
                        await channel.send(msg)
                        self.checked_assignments.add(key)
                    # Lembretes de 7, 3, 1 dia (apenas uma vez por dia/atividade)
                    dias_para_prazo = (due_dt.date() - today).days
                    reminder_key = (course['id'], a['name'], a['due'], dias_para_prazo)
                    if dias_para_prazo in [7, 3, 1] and reminder_key not in self.sent_reminders:
                        msg = (
                            f'@everyone\n'
                            f'⏰ **Faltam {dias_para_prazo} dia{"s" if dias_para_prazo > 1 else ""} para o prazo!**\n'
                            f'Curso: **{course["name"]}**\n'
                            f'Atividade: **{a["name"]}**\n'
                            f'Prazo: `{a["due"]}`\n'
                            f'{tempo_falta_str}'
                        )
                        await channel.send(msg)
                        self.sent_reminders.add(reminder_key)
            print('[DiscordBot] Verificação de tarefas concluída.')

            # Mostra o horário da próxima execução (após o término do loop)
            next_run = self.check_assignments.next_iteration
            if next_run is not None:
                import pytz
                br_tz = pytz.timezone('America/Sao_Paulo')
                next_run_br = next_run.astimezone(br_tz)
                print(f'[DiscordBot] Próxima verificação em {next_run_br.strftime("%d/%m/%Y %H:%M:%S")} (horário de Brasília)')
        except Exception as e:
            print(f'[DiscordBot] Erro ao checar prazos: {e}')
