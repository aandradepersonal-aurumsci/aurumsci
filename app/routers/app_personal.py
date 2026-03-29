"""
Router — App Personal
POST /app-personal/chat — chatbot AURI para o personal
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Personal
from app.utils.auth import get_personal_atual

router = APIRouter(prefix="/app-personal", tags=["App Personal"])

class ChatPersonalSchema(BaseModel):
    mensagem: str
    historico: Optional[List[dict]] = []

@router.post("/chat")
async def chat_personal(dados: ChatPersonalSchema, personal: Personal = Depends(get_personal_atual), db: Session = Depends(get_db)):
    from app.motor.ia_chatbot import responder_chatbot
    
    contexto = f"""Personal Trainer: {personal.nome}
CREF: {personal.cref or 'não informado'}
Você está conversando com um personal trainer profissional.
Ajude com gestão de alunos, protocolos de treino, periodização, nutrição esportiva e ciência do exercício.
Seja técnico, direto e baseado em evidências científicas."""

    resposta = await responder_chatbot(
        mensagem=dados.mensagem,
        historico=dados.historico or [],
        contexto=contexto,
        nome_personal=personal.nome
    )
    return {"resposta": resposta}
