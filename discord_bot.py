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
        self.sent_reminders = set()  # (assignment_url, dias_para_prazo)
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
                if due_dt and due_dt >= now:
                    self.checked_assignments.add(a['url'])
                    # Usa sempre o nome já tratado do client
                    msg_lines.append(f'**{a["name"]}**\nVencimento: `{a["due"]}`\n[Ver tarefa]({a["url"]})')
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
                    key = a['url']
                    link_md = f'[Ver tarefa]({a["url"]})' if a["url"] else ''
                    delta = due_dt - now
                    dias = delta.days
                    horas, resto = divmod(delta.seconds, 3600)
                    minutos = resto // 60
                    tempo_falta_str = f"Faltam {dias}d {horas}h {minutos}m para o prazo."
                    # Nova atividade
                    if key not in self.checked_assignments:
                        msg = self.message_ai.generate_assignment_message(
                            tipo="nova",
                            curso=course["name"],
                            atividade=a["name"],
                            prazo=a["due"],
                            tempo_falta_str=tempo_falta_str
                        )
                        msg = f'@everyone\n{msg}\n{link_md}'
                        await channel.send(msg)
                        self.checked_assignments.add(key)
                    dias_para_prazo = (due_dt.date() - today).days
                    reminder_key = (a['url'], dias_para_prazo)
                    lembrete_6h_key = (a['url'], '6h')
                    lembrete_enviado = False
                    # Lembrete de 1 ou 3 dias (se faltar mais de 6h)
                    if dias_para_prazo in [3, 1] and reminder_key not in self.sent_reminders and delta.total_seconds() > 6 * 3600:
                        msg = self.message_ai.generate_assignment_message(
                            tipo="lembrete",
                            curso=course["name"],
                            atividade=a["name"],
                            prazo=a["due"],
                            tempo_falta_str=tempo_falta_str
                        )
                        msg = f'@everyone\n{msg}\n{link_md}'
                        await channel.send(msg)
                        self.sent_reminders.add(reminder_key)
                        lembrete_enviado = True
                    # Lembrete especial para <= 6 horas
                    if delta.total_seconds() <= 6 * 3600 and delta.total_seconds() > 0 and lembrete_6h_key not in self.sent_reminders:
                        msg = self.message_ai.generate_assignment_message(
                            tipo="6h",
                            curso=course["name"],
                            atividade=a["name"],
                            prazo=a["due"],
                            tempo_falta_str=tempo_falta_str
                        )
                        msg = f'@everyone\n{msg}\n{link_md}'
                        await channel.send(msg)
                        self.sent_reminders.add(lembrete_6h_key)
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
