import requests
from bs4 import BeautifulSoup
import sys

class MoodleClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.login_url = f"{self.base_url}/login/index.php"
        self.username = username
        self.password = password
        self.session = requests.Session()
        print(f'[MoodleClient] Inicializado para {self.base_url} com usuário {self.username}')

    def login(self):
        print('[MoodleClient] Iniciando login...')
        resp = self.session.get(self.login_url)
        print(f'[MoodleClient] Status code GET login page: {resp.status_code}')
        print(f'[MoodleClient] URL após GET: {resp.url}')
        soup = BeautifulSoup(resp.text, 'html.parser')
        token_tag = soup.find('input', {'name': 'logintoken'})
        if not token_tag:
            print('[MoodleClient] logintoken NÃO encontrado no HTML da página de login!')
            print('[MoodleClient] Primeiros 1000 caracteres do HTML retornado:')
            print(resp.text[:1000])
            raise Exception('Não foi possível encontrar o logintoken na página de login do Moodle.')
        token = token_tag['value']

        payload = {
            'username': self.username,  # usa exatamente como está no .env
            'password': self.password,
            'logintoken': token,
        }
        masked_payload = payload.copy()
        masked_payload['password'] = '*' * len(masked_payload['password'])
        print(f'[MoodleClient] Payload de login: {masked_payload}')

        login_resp = self.session.post(self.login_url, data=payload)
        if 'login/index.php' in login_resp.url:
            print('[MoodleClient] Login falhou!')
            print(f'[MoodleClient] URL após login: {login_resp.url}')
            print(f'[MoodleClient] Conteúdo da resposta:\n{login_resp.text[:1000]}')
            # Tenta extrair mensagem de erro do HTML
            soup = BeautifulSoup(login_resp.text, 'html.parser')
            error_div = soup.find('div', {'class': 'loginerrors'})
            if error_div:
                print(f'[MoodleClient] Mensagem de erro do Moodle: {error_div.get_text(strip=True)}')
            else:
                print('[MoodleClient] Nenhuma mensagem de erro específica encontrada.')
            raise Exception('Login falhou, verifica usuário/senha!')
        print('[MoodleClient] Logado com sucesso!')

    def get_courses(self):
        print('[MoodleClient] Buscando cursos...')
        dashboard_url = f"{self.base_url}/my/"
        resp = self.session.get(dashboard_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        courses = []

        course_links = soup.select('a[href*="/course/view.php?id="]')
        seen = set()
        for link in course_links:
            href = link['href']
            if href not in seen:
                seen.add(href)
                course_id = href.split('id=')[-1]
                name = link.get_text(strip=True)
                courses.append({'id': course_id, 'name': name})
        print(f'[MoodleClient] {len(courses)} cursos encontrados.')
        return courses

    def get_activity_real_name(self, activity_url):
        #print(f"[DEBUG] Buscando nome da atividade em: {activity_url}", flush=True)
        resp = self.session.get(activity_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        yui_div = soup.find(lambda tag: tag.name == "div" and tag.has_attr("id") and tag["id"].startswith("yui_"))
        if yui_div:
            h2 = yui_div.find('h2')
            if h2:
                name = h2.get_text(strip=True)
                # print(f"[DEBUG] Nome extraído (yui_div h2): {name}", flush=True)
                return name
        # print("[DEBUG] Tentando .activity-header h2...", flush=True)
        activity_header = soup.select_one('.activity-header h2')
        if activity_header:
            name = activity_header.get_text(strip=True)
            # print(f"[DEBUG] Nome extraído (activity-header h2): {name}", flush=True)
            return name
        # print("[DEBUG] Tentando .activityinstance a span.instancename...", flush=True)
        instance_name = soup.select_one('.activityinstance a span.instancename')
        if instance_name:
            name = instance_name.get_text(strip=True)
            # print(f"[DEBUG] Nome extraído (activityinstance instancename): {name}", flush=True)
            return name
        # print("[DEBUG] Tentando .activity-header h2 fallback...", flush=True)
        activity_header_h2 = soup.select_one('.activity-header h2')
        if activity_header_h2:
            name = activity_header_h2.get_text(strip=True)
            # print(f"[DEBUG] Nome extraído (activity-header h2 fallback): {name}", flush=True)
            return name
        og = soup.find('meta', property='og:title')
        if og and og.has_attr('content'):
            name = og['content'].strip()
            # print(f"[DEBUG] Nome extraído (og:title): {name}", flush=True)
            return name
        # print("[DEBUG] Tentando fallback <title>...", flush=True)
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            if ':' in title_text:
                name = title_text.split(':', 1)[1].split('|')[0].strip()
            else:
                name = title_text
            # print(f"[DEBUG] Nome extraído (title): {name}", flush=True)
            return name
        # print("[DEBUG] Tentando main_content h1...", flush=True)
        main_content = soup.find('div', id='page-content') or soup.find('div', role='main')
        if main_content:
            h1 = main_content.find('h1')
            if h1:
                name = h1.get_text(strip=True)
                # print(f"[DEBUG] Nome extraído (main_content h1): {name}", flush=True)
                return name
        # print("[DEBUG] Tentando page-header-headings h1...", flush=True)
        header = soup.find('div', class_='page-header-headings')
        if header:
            h1 = header.find('h1')
            if h1:
                name = h1.get_text(strip=True)
                # print(f"[DEBUG] Nome extraído (page-header-headings h1): {name}", flush=True)
                return name
        # print("[DEBUG] Tentando primeiro h1...", flush=True)
        h1 = soup.find('h1')
        if h1:
            name = h1.get_text(strip=True)
            # print(f"[DEBUG] Nome extraído (primeiro h1): {name}", flush=True)
            return name
        # fallback final
        # print('[DEBUG] Nenhum nome de atividade encontrado.', flush=True)
        # print('[DEBUG] Primeiros 1000 caracteres do HTML da atividade:', flush=True)
        # print(resp.text[:1000], flush=True)
        return None

    def get_assignment_due_date(self, activity_url):
       #print(f"[DEBUG] Buscando data de vencimento em: {activity_url}", flush=True)
        resp = self.session.get(activity_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup.find_all(string=True):
            if tag and isinstance(tag, str) and "Vencimento:" in tag:
                text = tag.strip()
                idx = text.find("Vencimento:")
                if idx != -1:
                    venc = text[idx + len("Vencimento:"):].strip()
                    if venc:
                        # print(f"[DEBUG] Data de vencimento encontrada (Vencimento: ...): {venc}", flush=True)
                        return venc
        for strong in soup.find_all(['strong', 'b']):
            if strong.get_text(strip=True).startswith("Vencimento:"):
                next_text = strong.next_sibling
                if next_text and isinstance(next_text, str):
                    venc = next_text.strip()
                    if venc:
                        # print(f"[DEBUG] Data de vencimento encontrada (<strong>/<b>): {venc}", flush=True)
                        return venc
        due_labels = ["Due date", "Prazo final", "Data de entrega"]
        for label in due_labels:
            due_elem = soup.find(lambda tag: tag.name in ["td", "th", "div", "span"] and label in tag.get_text())
            if due_elem:
                next_td = due_elem.find_next("td")
                if next_td:
                    due_text = next_td.get_text(strip=True)
                    # print(f"[DEBUG] Data de vencimento encontrada (tabela): {due_text}", flush=True)
                    return due_text
                due_text = due_elem.get_text(strip=True)
                # print(f"[DEBUG] Data de vencimento encontrada (tabela fallback): {due_text}", flush=True)
                return due_text
        # print("[DEBUG] Nenhuma data de vencimento encontrada.", flush=True)
        return "-"

    def get_assignments(self, course_id):
        # print(f"[DEBUG] Buscando atividades para o curso {course_id}", flush=True)
        course_url = f"{self.base_url}/course/view.php?id={course_id}"
        resp = self.session.get(course_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        assignments = []

        # print(f"[DEBUG] Conteúdo da página do curso (trecho): {resp.text[:500]}", flush=True)

        assign_links = soup.find_all('a', href=lambda href: href and '/mod/assign/view.php?id=' in href)
        # print(f"[DEBUG] Encontrados {len(assign_links)} links para atividades do tipo assign", flush=True)

        seen = set()
        for i, link in enumerate(assign_links):
            activity_url = link['href']
            if activity_url.startswith('/'):
                activity_url = self.base_url + activity_url
            if activity_url in seen:
                continue
            seen.add(activity_url)
            # print(f"[DEBUG] Processando atividade {i+1}: {activity_url}", flush=True)
            name = self.get_activity_real_name(activity_url) or link.get_text(strip=True)
            if not name.strip():
                name = f"Atividade {i+1} (Sem nome)"
                # print(f"[DEBUG] Nome vazio - usando fallback: '{name}'", flush=True)
            due = self.get_assignment_due_date(activity_url)
            # print(f"[DEBUG] Nome final: '{name}' | Vencimento: '{due}'", flush=True)
            assignments.append({'name': name, 'due': due, 'url': activity_url})

        return assignments

    def print_all_courses_and_assignments(self):
        print('\n=== Lista de cursos e atividades ===')
        courses = self.get_courses()
        for course in courses:
            print(f'Curso: {course["name"]} (ID: {course["id"]})')
            assignments = self.get_assignments(course['id'])
            if assignments:
                for a in assignments:
                    print(f'  - Atividade: {a["name"]} (Vencimento: {a["due"]})')
            else:
                print('  - Nenhuma atividade encontrada.')
        print('=== Fim da lista ===\n')
