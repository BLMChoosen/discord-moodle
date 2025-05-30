# Bot do Discord para Avisar Prazos do Moodle

## O que é isso?

Esse é um bot do Discord que faz login automático no Moodle do IFRS Campus Farroupilha com seu usuário, puxa as atividades e seus prazos e avisa a galera no servidor quando os prazos estiverem chegando. Tudo no modo automático, sem você precisar ficar entrando no Moodle toda hora.

## Como funciona?

* O bot faz login no Moodle usando seu usuário e senha, mantendo a sessão com cookies.
* Ele acessa a página das atividades do curso, faz um parse no HTML pra extrair os nomes e prazos das tarefas.
* Você pode configurar pra ele mandar mensagens no Discord avisando quando o prazo estiver perto.
* O bot roda em Python usando as bibliotecas `requests`, `beautifulsoup4` e `discord.py`.

## Requisitos

* Python 3.7 ou superior
* Conta no Moodle com acesso às atividades do curso
* Token do bot do Discord configurado

## Como usar

1. Instale as dependências:

```
pip install -r requirements.txt
```

2. Configure o arquivo `.env` com seu usuário, senha e token do bot do Discord.

3. Configure o token do bot do Discord e o canal onde ele deve mandar as mensagens.

4. Rode o script:

```
python main.py
```

## Avisos importantes

* Login automático pode ser bloqueado pelo Moodle ou pela escola.
* A estrutura do HTML do Moodle pode mudar, o que pode quebrar o parsing das atividades.
* Use com responsabilidade e respeite as regras da sua instituição.

---

## 🛠️ Como configurar o bot no Discord?

1. **Crie a aplicação no Discord Developer Portal**

Acesse: [https://discord.com/developers/applications](https://discord.com/developers/applications)

Clique em **New Application** e dê um nome para ela.

2. **Adicione um bot à aplicação**

Dentro da aplicação criada, vá até a aba **Bot**.

Clique em **Add Bot** → **Yes, do it!**

Aqui, você verá o Token do bot. Copie esse token (guarde bem, ele será usado no código, mas não compartilhe com ninguém!).

3. **Configure as permissões do bot**

Ainda na aba **Bot**, ajuste as permissões (como leitura de mensagens, envio de mensagens, gerenciamento de mensagens, etc.), dependendo do que o seu bot precisa.

Ative as permissões:

* ✅ SERVER MEMBERS INTENT
* ✅ PRESENCE INTENT
* ✅ MESSAGE CONTENT INTENT

4. **Gere o link de convite**

Vá até a aba **OAuth2** → **URL Generator**.

Em **Scopes**, selecione **bot**.

Em **Bot Permissions**, marque as permissões necessárias (ex.: Send Messages, Read Messages, Manage Messages).

Copie o link gerado e cole no navegador para adicionar o bot ao seu servidor.

## Como copiar o ID de um canal no Discord

Para configurar corretamente onde o bot vai mandar as mensagens, você vai precisar do ID do canal no Discord. Aqui está o passo a passo:

1️⃣ **Ative o Modo de Desenvolvedor**

* Abra o Discord.
* Clique no ícone de engrenagem (⚙️) no canto inferior esquerdo para abrir as Configurações de Usuário.
* Vá até a aba "Avançado".
* Ative a opção **Modo de Desenvolvedor**.

2️⃣ **Copie o ID do Canal**

* Vá até o servidor onde você quer que o bot envie mensagens.
* Clique com o botão direito no canal de texto desejado.
* Clique em **Copiar ID**.

Pronto! Agora cole esse ID no arquivo de configuração (como o `.env` ou outro que você esteja usando) para que o bot saiba para qual canal mandar as notificações.

Se tiver dúvidas, dá uma olhada na [documentação oficial do Discord](https://support.discord.com/hc/pt-br/articles/206346498) para mais detalhes.

