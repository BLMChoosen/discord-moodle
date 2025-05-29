import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

class MoodleClient:
    def __init__(self, base_url, username, password, course_id):
        self.base_url = base_url.rstrip('/')
        self.login_url = f"{self.base_url}/login/index.php"
        self.course_id = course_id
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        login_page = self.session.get(self.login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        token_tag = soup.find('input', {'name': 'logintoken'})
        login_token = token_tag['value'] if token_tag else ''

        payload = {
            'username': self.username,
            'password': self.password,
            'logintoken': login_token,
        }

        resp = self.session.post(self.login_url, data=payload)
        if 'login/index.php' in resp.url:
            raise Exception('Login falhou, verifica usuário/senha!')
        print('[MoodleClient] Logado com sucesso!')

    def get_assignments(self):
        atividades_url = f"{self.base_url}/mod/assign/index.php?id={self.course_id}"
        resp = self.session.get(atividades_url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        assignments = []
        activities = soup.find_all('tr', class_='assignment')  # Pode variar, ajusta isso!
        if not activities:
            # Tenta outro seletor, Moodle varia muito
            activities = soup.select('table.assignments tr')

        for a in activities:
            # Tenta extrair nome e prazo da atividade
            nome_tag = a.find('td', class_='c1') or a.find('td')
            prazo_tag = a.find('td', class_='c3') or a.find_all('td')[-1]

            if nome_tag and prazo_tag:
                nome = nome_tag.get_text(strip=True)
                prazo = prazo_tag.get_text(strip=True)
                assignments.append({'name': nome, 'due': prazo})
        return assignments
