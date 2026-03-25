# ia_chatbot.py - AurumSci

def montar_contexto(aluno: dict) -> str:
    return f"Aluno: {aluno.get('nome', 'Aluno')}"

def resposta_rapida(mensagem: str) -> str:
    return "Olá! Sou a AURI. Como posso ajudar?"

def responder_chat(mensagem: str, contexto: dict = {}) -> str:
    return "Olá! Sou a AURI, sua assistente de treino!"

def responder_chatbot(mensagem: str, contexto: dict = {}) -> str:
    return "Olá! Sou a AURI, sua assistente de treino!"
