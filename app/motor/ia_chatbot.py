# ia_chatbot.py - AurumSci AURI
import anthropic
import asyncio

import os
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def montar_contexto(aluno: dict, avaliacoes: list = [], treino: dict = {}, anamnese: dict = {}, presencas: dict = {}) -> str:
    ctx = f"Aluno: {aluno.get('nome', 'Aluno')}\n"
    ctx += f"Objetivo: {aluno.get('objetivo', 'hipertrofia')}\n"
    ctx += f"Nível: {aluno.get('nivel', 'iniciante')}\n"
    if avaliacoes:
        a = avaliacoes[0]
        ctx += f"Última avaliação: peso {a.get('peso')}kg, gordura {a.get('percentual_gordura')}%\n"
    if treino:
        ctx += f"Plano ativo: {treino.get('nome')} — objetivo: {treino.get('objetivo')}\n"
    if presencas:
        ctx += f"Frequência últimos 30 dias: {presencas.get('frequencia_pct')}%\n"
    return ctx

def resposta_rapida(mensagem: str, aluno: dict = {}) -> str:
    return None

async def responder_chatbot(mensagem: str, historico: list = [], contexto: str = "", nome_personal: str = "seu personal") -> str:
    system = f"""Você é AURI, assistente de treino inteligente da plataforma AurumSci.
Você é especialista em ciência do exercício, hipertrofia, nutrição esportiva e periodização.
Responda de forma direta, motivadora e baseada em evidências científicas.
Sempre personalize suas respostas com base no perfil do aluno.

PERFIL DO ALUNO:
{contexto}

Seja conciso (máximo 3 parágrafos), use linguagem acessível e sempre encoraje o aluno."""

    msgs = []
    for h in historico[-10:]:
        if h.get("role") and h.get("content"):
            msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": mensagem})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=system,
            messages=msgs
        )
        return response.content[0].text
    except Exception as e:
        return f"Desculpe, tive um problema técnico. Tente novamente! ({str(e)[:50]})"
