import requests
from bs4 import BeautifulSoup

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

    def get_assignments(self, course_id):
        print(f'[MoodleClient] Buscando tarefas para o curso {course_id}...')
        assign_url = f"{self.base_url}/mod/assign/index.php?id={course_id}"
        resp = self.session.get(assign_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        assignments = []

        rows = soup.select('table.generaltable tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                due = cols[2].get_text(strip=True)
                assignments.append({'name': name, 'due': due})
        print(f'[MoodleClient] {len(assignments)} tarefas encontradas para o curso {course_id}.')
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
