# Aqui vai a bagaça da IA que vai criar mensagens personalizadas, falta importar as apis e tudo mais
# Por enquanto, um stub básico com mensagem fake.

def generate_message(course_name, assignment):
    """
    Recebe:
        - course_name: nome do curso
        - assignment: dict com 'name' e 'due'
    Retorna:
        - string com a mensagem formatada
    """

    # Exemplo simples — depois vou integrar com uma IA de verdade
    msg = (f"⚠️ Atenção! No curso **{course_name}**, a atividade "
           f"**{assignment['name']}** vence em **{assignment['due']}**. "
           "Corre pra não perder o prazo, porra!")
    return msg
