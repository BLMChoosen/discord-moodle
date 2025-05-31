from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

API_KEY = os.getenv('AI_API_KEY') or os.getenv('API_KEY')

client = genai.Client(api_key=API_KEY)

def generate_assignment_message(
    tipo,  # "nova", "lembrete", "6h"
    curso,
    atividade,
    prazo,
    tempo_falta_str
):
    """
    Gera uma mensagem personalizada para o Discord usando Gemini.
    tipo: "nova", "lembrete", "6h"
    """
    if tipo == "nova":
        prompt = (
            f"Crie uma mensagem curta e clara para Discord avisando que uma nova tarefa foi lançada no curso '{curso}', "
            f"atividade '{atividade}', com prazo '{prazo}'. "
            f"Inclua o tempo restante: {tempo_falta_str}. "
            f"Seja objetivo, amigável e incentive o aluno a não perder o prazo. "
            f"Use tom motivacional e direto, sem enrolação."
        )
    elif tipo == "lembrete":
        prompt = (
            f"Crie uma mensagem de lembrete para Discord avisando que falta pouco tempo para o prazo da atividade '{atividade}' "
            f"do curso '{curso}', com prazo '{prazo}'. "
            f"Inclua o tempo restante: {tempo_falta_str}. "
            f"Seja objetivo, amigável e incentive o aluno a entregar a tarefa. "
            f"Use tom motivacional e direto, sem enrolação."
        )
    elif tipo == "6h":
        prompt = (
            f"Crie uma mensagem URGENTE para Discord, avisando que faltam menos de 6 horas para o prazo da atividade '{atividade}' "
            f"do curso '{curso}', que expira em '{prazo}'. "
            f"Mostre o tempo restante: {tempo_falta_str}. "
            f"Comece com URGENTE em caixa alta, chame o aluno para entregar agora mesmo, seja direto e motivacional, "
            f"exemplo de tom: 'URGENTE: PRAZO FINAL EM 1 HORA E 52 MINUTOS! Aluno(a), a atividade ... expira HOJE ... NÃO PERCA ESSA CHANCE! ... ENTREGUE AGORA MESMO!'."
        )
    else:
        prompt = (
            f"Mensagem de aviso para atividade '{atividade}' do curso '{curso}', prazo '{prazo}'. "
            f"Tempo restante: {tempo_falta_str}."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction="Você é um bot de avisos de prazos do Moodle para estudantes."),
            contents=[prompt]
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"[ERRO IA] {prompt}"
