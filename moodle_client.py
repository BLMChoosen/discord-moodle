import requests
from bs4 import BeautifulSoup

class MoodleClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.login_url = f"{self.base_url}/login/index.php"
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        resp = self.session.get(self.login_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        token_tag = soup.find('input', {'name': 'logintoken'})
        token = token_tag['value'] if token_tag else ''

        payload = {
            'username': self.username,
            'password': self.password,
            'logintoken': token,
        }

        login_resp = self.session.post(self.login_url, data=payload)
        if 'login/index.php' in login_resp.url:
            raise Exception('Login falhou, verifica usuário/senha!')
        print('[MoodleClient] Logado com sucesso!')

    def get_courses(self):
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
        return courses

    def get_assignments(self, course_id):
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
        return assignments
