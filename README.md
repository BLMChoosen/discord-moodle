# Bot do Discord para Avisar Prazos do Moodle

## O que é isso?

Esse é um bot do Discord que faz login automático no Moodle do IFRS Campus Farroupilha com seu usuário, puxa as atividades e seus prazos e avisa a galera no servidor quando os prazos estiverem chegando. Tudo no modo automático, sem você precisar ficar entrando no Moodle toda hora.

## Como funciona?

- O bot faz login no Moodle usando seu usuário e senha, mantendo a sessão com cookies.
- Ele acessa a página das atividades do curso, faz um parse no HTML pra extrair os nomes e prazos das tarefas.
- Você pode configurar pra ele mandar mensagens no Discord avisando quando o prazo estiver perto.
- O bot roda em Python usando as bibliotecas `requests`, `beautifulsoup4` e `discord.py`.

## Requisitos

- Python 3.7 ou superior
- Conta no Moodle com acesso às atividades do curso
- Token do bot do Discord configurado

## Como usar

1. Instale as dependências:
```
pip install -r requirements.txt
```
2. Configure o .env com seu usuário, senha e URL do Moodle, além do ID do curso que você quer monitorar.

3. Configure o token do bot do Discord e o canal onde ele deve mandar as mensagens.

4. Rode o script:
```
python main.py
```
## Avisos importantes

- Login automático pode ser bloqueado pelo Moodle ou pela escola.
- A estrutura do HTML do Moodle pode mudar, o que pode quebrar o parsing das atividades.
- Use com responsabilidade e respeite as regras da sua instituição.

---
